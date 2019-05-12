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
                            batch_size,
                            crop_size,
                            shuffle=True, num_workers=num_workers)

       
    generator = Generator(attention_dim, embedding_size, lstm_size, vocab_size, load=args.load)
    generator = generator.to(device)
    generator = generator.eval()


    fullnames = ['data/giraffe.png', 'data/surf.jpg', 'data/bedroom.jpg']
    for fullname in fullnames:
        print(fullname.split('/')[-1].split('.')[0] + ':')
        print(generator.inference(vocab, img_path=fullname, translate_flag=True))
        #print(caption = generator.generate(fullname, vocab, False))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--load', type=str, default='pre', help='which model to load')
    args = parser.parse_args()
    main(args)
