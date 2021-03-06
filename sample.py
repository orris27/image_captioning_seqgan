import torch
import torch.utils.data as data
import os
import pickle
import numpy as np
import nltk
from build_vocab import Vocabulary

from dataloader import get_loader
from generator import Generator
from settings import *


def main(args):
    with open(vocab_path, 'rb') as f:
        vocab = pickle.load(f)

    vocab_size = len(vocab)
    print('vocab_size:', vocab_size)

    dataloader = get_loader(image_dir, caption_path, vocab, 
                            args.batch_size,
                            crop_size,
                            shuffle=True, num_workers=num_workers)

       
    generator = Generator(attention_dim, embedding_size, lstm_size, vocab_size, load_path=args.g_path, noise=args.noise)
    generator = generator.to(device)
    generator = generator.eval()

    
    for filename in os.listdir(args.image_dir):
        fullname = os.path.join(args.image_dir, filename)
        print(fullname.split('/')[-1].split('.')[0] + ':')
        caption_set = set()
        max_iter = 50
        while len(caption_set) != 3 and max_iter != 0: # must generate 3 unique results
            caption_set.add(generator.inference(vocab, img_path=fullname, translate_flag=True))
            max_iter -= 1
        for caption in caption_set:
            print(caption)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--g_path', type=str, default='data/generator_params.pkl', help='which model to load') # 'pre' or 'ad'
    parser.add_argument('--image_dir', type=str, default='data/images', help='')
    parser.add_argument('--batch_size', type=int, default=16, help='')
    parser.add_argument('--noise', type=bool, default=False, help='')
    args = parser.parse_args()
    main(args)
