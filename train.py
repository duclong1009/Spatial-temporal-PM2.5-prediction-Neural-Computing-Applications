import argparse
import torch
import torch.nn as nn
import numpy as np
import random
from tqdm.notebook import tqdm

# from torch.utils.tensorboard import SummaryWriter
import matplotlib.pyplot as plt
import pandas as pd
from utils.ultilities import config_seed, save_checkpoint, EarlyStopping
from utils.loader import get_columns, preprocess_pipeline, AQDataSet
from torch.utils.data import DataLoader
from models.stdgi import STDGI
from layers.decoder import Decoder
from modules.train.train import train_decoder_fn
from modules.train.train import train_stdgi_fn

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=bool, default=True)
    parser.add_argument("--test", type=bool, default=False)
    parser.add_argument("--seed", default=52, type=int, help="Seed")
    parser.add_argument("--target_station", default=14, type=int)
    parser.add_argument(
        "--train_station",
        default=[i for i in range(28)],
        type=list,
    )
    parser.add_argument("--input_dim", default=1, type=int)
    parser.add_argument("--output_dim", default=1, type=int)
    parser.add_argument("--num_epochs_stdgi", default=10, type=int)
    parser.add_argument("--num_epochs_decoder", default=10, type=int)
    parser.add_argument("--batch_size", default=32, type=int)
    parser.add_argument("--lr_stdgi", default=5e-3, type=float)
    parser.add_argument("--lr_decoder", default=5e-3, type=float)
    parser.add_argument("--load_model", default=False)
    parser.add_argument("--output_stdgi", default=60, type=int)
    parser.add_argument("--checkpoint_file", default="./checkpoint/stdgi/", type=str)
    parser.add_argument("--visualize_dir", default="./output/visualize/", type=str)
    parser.add_argument("--path_model", default="", type=str)
    parser.add_argument("--en_hid1", default=400, type=int)
    parser.add_argument("--en_hid2", default=400, type=int)
    parser.add_argument("--dis_hid", default=6, type=int)
    parser.add_argument("--act_fn", default="relu", type=str)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    config_seed(args.seed)
    device = torch.device("cpu")
    file_path = "./data/"
    # Preprocess and Load data
    location = pd.read_csv(file_path + "locations.csv").to_numpy()
    location = location[:, 1:]
    res, res_rev, pm_df = get_columns(file_path)
    trans_df, scaler = preprocess_pipeline(pm_df)
    train_dataset = AQDataSet(
        data_df=trans_df[:50],
        location_df=location,
        list_train_station=args.train_station,
        input_dim=args.input_dim,
        output_dim=args.output_dim,
    )
    train_dataloader = DataLoader(
        train_dataset, batch_size=args.batch_size, shuffle=True
    )

    # Model Stdgi
    stdgi = STDGI(
        args.input_dim,
        args.output_stdgi,
        args.en_hid1,
        args.en_hid2,
        args.dis_hid,
        args.act_fn,
    ).to(device)

    l2_coef = 0.0
    mse_loss = nn.MSELoss()
    bce_loss = nn.BCELoss()
    stdgi_optimizer = torch.optim.Adam(
        stdgi.parameters(), lr=args.lr_stdgi, weight_decay=l2_coef
    )

    early_stopping_stdgi = EarlyStopping(patience=3, verbose=True, delta=0.02)
    train_stdgi_loss = []
    for i in range(args.num_epochs_stdgi):
        if not early_stopping_stdgi.early_stop:
            loss = train_stdgi_fn(
                stdgi, train_dataloader, stdgi_optimizer, bce_loss, device
            )
            early_stopping_stdgi(loss, stdgi)
            print("Epochs/Loss: {}/ {}".format(i, loss))
    print("train xong stdgi")
    decoder = Decoder(
        args.input_dim + args.output_stdgi,
        args.output_dim,
        n_layers_rnn=1,
        rnn="GRU",
        cnn_hid_dim=128,
        fc_hid_dim=64,
    ).to(device)
    optimizer_decoder = torch.optim.Adam(
        decoder.parameters(), lr=args.lr_decoder, weight_decay=l2_coef
    )
    train_decoder_loss = []
    early_stopping_decoder = EarlyStopping(
        patience=3, verbose=True, delta=0, path="test_decoder.pt"
    )
    print("train decoder")
    for i in range(args.num_epochs_decoder):
        if not early_stopping_decoder.early_stop:
            epoch_loss = train_decoder_fn(
                stdgi, decoder, train_dataloader, mse_loss, optimizer_decoder, device
            )
            early_stopping_decoder(epoch_loss,decoder)
            print("Epochs/Loss: {}/ {}".format(i, epoch_loss))
        # save_checkpoint(decoder, optimizer, f"../checkpoint/decoder/deocder_epoch_{i}")
        train_decoder_loss.append(epoch_loss)
