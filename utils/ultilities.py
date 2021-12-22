import matplotlib.pyplot as plt
import numpy as np
import torch
import random


def config_seed(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)


def save_checkpoint(model, path):
    checkpoints = {
        "model_dict": model.state_dict(),
    }
    torch.save(checkpoints, path)


def load_model(model, checkpoint_path):
    model.load_state_dict(torch.load(checkpoint_path)["model_dict"])


def visualize(train_loss, val_loss, args):
    plt.plot(
        train_loss["epoch"],
        train_loss["train_loss"],
        label="Training loss",
        linestyle="-.",
    )
    plt.plot(
        val_loss["epoch"], val_loss["val_loss"], label="Validation loss", linestyle=":"
    )
    plt.legend()
    plt.label("Training vs validation loss")
    plt.savefig(args.visualize_dir)


class EarlyStopping:
    """Early stops the training if validation loss doesn't improve after a given patience."""

    def __init__(
        self, patience=3, verbose=False, delta=0, path="checkpoint.pt", trace_func=print
    ):
        """
        Args:
            patience (int): How long to wait after last time validation loss improved.
                            Default: 7
            verbose (bool): If True, prints a message for each validation loss improvement.
                            Default: False
            delta (float): Minimum change in the monitored quantity to qualify as an improvement.
                            Default: 0
            path (str): Path for the checkpoint to be saved to.
                            Default: 'checkpoint.pt'
            trace_func (function): trace print function.
                            Default: print
        """
        self.patience = patience
        self.verbose = verbose
        self.counter = 0
        self.best_score = None
        self.early_stop = False
        self.val_loss_min = np.Inf
        self.delta = delta
        self.path = path
        self.trace_func = trace_func

    def __call__(self, val_loss, model):

        score = val_loss

        if self.best_score is None:
            self.best_score = score
            self.save_checkpoint(val_loss, model)
        elif score + self.delta > self.best_score:
            self.counter += 1
            self.trace_func(
                f"EarlyStopping counter: {self.counter} out of {self.patience}"
            )
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_score = score
            self.save_checkpoint(val_loss, model)
            self.counter = 0

    def save_checkpoint(self, val_loss, model):
        """Saves model when validation loss decrease."""
        if self.verbose:
            self.trace_func(
                f"Validation loss decreased ({self.val_loss_min:.6f} --> {val_loss:.6f}).  Saving model ..."
            )
        checkpoints = {"model_dict": model.state_dict()}
        torch.save(checkpoints, self.path)
        self.val_loss_min = val_loss
