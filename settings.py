import torch 

#image_dir = 'data/resized2014'
image_dir = '/content/resized2014'
caption_path = '/content/annotations/captions_train2014.json'
encoder_path = 'data/encoder_params.pkl'
decoder_path = 'data/decoder_params.pkl'
vocab_path = 'data/vocab.pkl'
discriminator_path = 'data/discriminator_params.pkl'

#batch_size = 16
num_workers = 2
crop_size = 224
#embedding_size = 256 # May 5, 2019
embedding_size = 512 # "Show and Tell A Neural Image Caption Generator" used 512 dimensions for the embeddingf size
lstm_size = 512 # "Show and Tell A Neural Image Caption Generator" used 512 dimensions for the size of LSTM memory
learning_rate = 1e-3
log_every = 10
num_epochs = 100
save_every = 100
alpha_c = 1.0 
attention_dim = 512
fine_tune_encoder = False
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

