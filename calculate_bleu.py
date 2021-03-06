import torch
import torch.utils.data as data
import os
import pickle
import numpy as np
import nltk
from build_vocab import Vocabulary
from pycocotools.coco import COCO
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence
import torchvision.transforms as T
from PIL import Image
from nltk.translate.bleu_score import sentence_bleu
import tqdm


from dataloader import get_loader
from generator import Generator
from settings import *


def main(args):

    with open(vocab_path, 'rb') as f:
        vocab = pickle.load(f)

    vocab_size = len(vocab)
    print('vocab_size:', vocab_size)

    transform = T.Compose([
        T.ToTensor(),
        T.Normalize((0.485, 0.456, 0.406),
                             (0.229, 0.224, 0.225))])

    #image_dir = './data/valresized2014/'
    #caption_path = './data/annotations/captions_val2014.json'
    num_workers = 0


    dataloader = get_loader(image_dir, caption_path, vocab, 
                            args.batch_size,
                            crop_size,
                            shuffle=False, num_workers=num_workers, transform=transform)


    generator = Generator(attention_dim, embedding_size, lstm_size, vocab_size, load_path=args.g_path, noise=args.noise)
    generator = generator.to(device)
    generator = generator.eval()

    def translate(indices, vocab):
        sentences = list()
        for index in indices:
            word = vocab.idx2word[int(index)]
            if word == '<eos>':
                break
            sentences.append(word)
        return ' '.join(sentences)

    scores = list()
    num_batches = 100
    print('total length:', len(dataloader), '; we chose %d batches'%(num_batches))
    def compute_nltk(dataloader, generator, num_batches):
        for index, (imgs, captions, lengths) in tqdm.tqdm(enumerate(dataloader)):
            imgs = imgs.to(device)

            features = generator.encoder(imgs)
            indices_list = generator.inference(vocab, features=features)
            for i in range(len(indices_list)):
                sentence_pred = translate(indices_list[i][1:], vocab)
                sentence = translate(captions[i][1:], vocab)
                bleus = list()
                for j in range(4):
                    weights = [0] * 4
                    weights[j] = 1
                    bleus.append(sentence_bleu([sentence], sentence_pred, weights=weights))
                scores.append(bleus)
            if index + 1 == num_batches:
                break

        scores = np.asarray(scores)
        print(scores.shape)

        for i in range(4):
            print("BLEU{}".format(i + 1))
            print('mean score:', np.sum(scores[:, i]) / scores.shape[0])
            print('min score:', np.min(scores[:, i]))
            print('max score:', np.max(scores[:, i]))
            print('sum score:', np.sum(scores[:, i]))
            
    #compute_nltk(dataloader, generator, num_batches)

    def write_to_file(dataloader, generator, num_batches):
        with open('data/hyp.txt', 'w') as hyp, open('data/ref.txt', 'w') as ref:
            for index, (imgs, captions, lengths) in tqdm.tqdm(enumerate(dataloader)):
                imgs = imgs.to(device)

                features = generator.encoder(imgs)
                indices_list = generator.inference(vocab, features=features)

                for i in range(len(indices_list)):
                    sentence_pred = translate(indices_list[i][1:], vocab)
                    sentence = translate(captions[i][1:], vocab)
                    sentence_pred = sentence_pred.strip('<sos> ').strip(' <eos>')
                    sentence = sentence.strip('<sos> ').strip(' <eos>')

                    hyp.write(sentence_pred + '\n')
                    ref.write(sentence + '\n')
                    hyp.flush()
                    ref.flush()
                    
                if index + 1 == num_batches:
                    break

    write_to_file(dataloader, generator, num_batches)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--g_path', type=str, default=None, help='the generator model to load')
    parser.add_argument('--batch_size', type=int, default=16, help='')
    parser.add_argument('--noise', type=bool, default=False, required=True, help='')
    args = parser.parse_args()
    main(args)

