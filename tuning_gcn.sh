python train_attention_stdgi_test_wo_ssa.py --input_dim 10 --stdgi_noise_min 0.4 --stdgi_noise_max 0.8 --name stdgi_tuning6464 --en_hid1 64 --en_hid2 64 --checkpoint_decoder decoder_tuning6464 --checkpoint_stdgi stdgi_tuning6464 --num_epochs_stdgi 1 --num_epochs_decoder 1 --model_type gede
# python traine2e.py --input_dim 9 --en_hid1 64 --en_hid2 64 --checkpoint_decoder decoder_tuning6464 --checkpoint_stdgi stdgi_tuning6464 --num_epochs_stdgi 30 --num_epochs_decoder 30 
