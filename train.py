# -----------------------------------------------------------------------
# train.py
# Trainer for a binarized CNN
#
# Creation Date   : 04/Aug./2017
# Copyright (C) <2017> Hiroki Nakahara, All rights reserved.
# 
# Released under the GPL v2.0 License.
# 
# Acknowledgements:
# This source code is based on following projects:
#
# Chainer binarized neural network by Daisuke Okanohara
# https://github.com/hillbig/binary_net
# Various CNN models including Deep Residual Networks (ResNet) 
#  for CIFAR10 with Chainer by mitmul
# https://github.com/mitmul/chainer-cifar10
# -----------------------------------------------------------------------

import argparse
#import cPickle as pickle # python 2.7
import _pickle as pickle # python 3.5
import numpy as np
import os
import chainer
from chainer import optimizers
from chainer import serializers
import net2 # it will be generated by the GUINNESS GUI

import trainer

import time
import weight_clip

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CIFAR-10 dataset trainer')
    parser.add_argument('--gpu', '-g', type=int, default=-1,
                        help='GPU device ID (negative value indicates CPU)')
    parser.add_argument('--model', '-m', type=str, default='bincnn', choices=['bincnn'],
                        help='Model name')
    parser.add_argument('--batch_size', '-b', type=int, default=20,
                        help='Mini batch size')
    parser.add_argument('--dataset', '-d', type=str, default='image.pkl',
                        help='Dataset image pkl file path')
    parser.add_argument('--label', '-l', type=str, default='label.pkl',
                        help='Dataset label pkl file path')
    parser.add_argument('--prefix', '-p', type=str, default='temp', # should be project name
                        help='Prefix of model parameter files')
    parser.add_argument('--iter', type=int, default=10,
                        help='Training iteration')
    parser.add_argument('--save_iter', type=int, default=0,
                        help='Iteration interval to save model parameter file.')
    parser.add_argument('--lr_decay_iter', type=int, default=100,
                        help='Iteration interval to decay learning rate')
    parser.add_argument('--weight_decay', type=float, default=0.0001,
                        help='Weight decay')
    parser.add_argument('--optimizer', type=str, default='sgd', choices=['sgd', 'adam', 'momentum', 'delta'],
                        help='Optimizer name')
    parser.add_argument('--lr', type=float, default=0.01,
                        help='Initial learning rate for SGD')
    parser.add_argument('--alpha', type=float, default=0.00005,
                        help='Initial alpha for Adam')
    parser.add_argument('--res_depth', type=int, default=18,
                        help='Depth of Residual Network')
    parser.add_argument('--skip_depth', action='store_true',
                        help='Use stochastic depth in Residual Network')
    parser.add_argument('--swapout', action='store_true',
                        help='Use swapout')
    parser.add_argument('--seed', type=int, default=1,
                        help='Random seed')
    parser.add_argument('--dim', type=int, default=3,
                        help='Dimension (default RGB, that is, 3)')
    parser.add_argument('--siz', type=int, default=32,
                        help='ImageSiz (default 32, that is, 32x32)')
    parser.add_argument('--guinness', type=str, default='./hoge', # should be project name
                        help='Prefix of model parameter files for the GUINNESS flow')
    parser.add_argument('--resume', type=str, default='no',
                        help='Resume traning, if pre-trained model exists')
    args = parser.parse_args()

    np.random.seed(args.seed)
    
    log_file_path = '{}_log.csv'.format(args.prefix)
#    lr_decay_iter = map(int, args.lr_decay_iter.split(','))

    if args.prefix is None:
        model_prefix = '{}_{}'.format(args.model, args.optimizer)
    else:
        model_prefix = args.prefix

    # load image dataset
    print('loading dataset %s' % args.dataset)
    with open(args.dataset, 'rb') as f:
        images = pickle.load(f)

        index = np.random.permutation(len(images['train']))        
        #threshold = np.int32(len(images['train'])/10*9)
        threshold = np.int32(len(images['train']))
        train_index = index[:threshold]
        valid_index = index[threshold:]

        train_x = images['train'][train_index].astype(np.float32)
        valid_x = images['train'][valid_index].astype(np.float32)
        test_x = images['test'].astype(np.float32)

    
    print("[INFO] #TRAIN DATA: %7d" % len(train_x))
    print("[INFO] #VALID DATA: %7d" % len(valid_x))
    print("[INFO] #TEST  DATA: %7d" % len(test_x))

    # load label dataset
    with open(args.label, 'rb') as f:
        labels = pickle.load(f)
        train_y = labels['train'][train_index].astype(np.int32)
        valid_y = labels['train'][valid_index].astype(np.int32)
        test_y = labels['test'].astype(np.int32)

    # generate testbench (test_img.txt) for C/C++ code
    idx = 0
    image = test_x
    
    # extract only one image
    image1 = image[idx]

    # generate text file as a bench marck
    bench_img = image1.transpose(1,2,0)
    bench_img = bench_img.reshape(-1,)

    fname = 'test_img.txt'
    print(' Test Image Fileout -> %s' % fname)
    np.savetxt(fname, bench_img,fmt="%.0f",delimiter=",")

    # start training
    print('start training')
    cifar_net = net2.CNN() # modified

    # resume pre-trained model, if exist
    if args.resume == 'yes':
        print(" Resume Pre-Trained Model")
        serializers.load_npz('{}.model'.format(model_prefix), cifar_net)


    if args.optimizer == 'sgd':
        print("optimizer: SGD")
        optimizer = optimizers.SGD(lr=args.lr)
    elif args.optimizer == 'momentum':
        print("optimizer: momentum SGD")
        optimizer = optimizers.MomentumSGD(lr=args.lr)
    elif args.optimizer == 'delta':
        print("optimizer: AdaDelta")
        optimizer = optimizers.AdaDelta()
    else:
        print("optimizer: Adam")
        optimizer = optimizers.Adam(alpha=args.alpha)
    optimizer.setup(cifar_net)
    if args.weight_decay > 0:
        optimizer.add_hook(chainer.optimizer.WeightDecay(args.weight_decay))

    optimizer.add_hook(weight_clip.WeightClip())

    cifar_trainer = trainer.CifarTrainer(cifar_net, optimizer, args.iter, args.batch_size, args.gpu)

    state = {'best_valid_error': 100, 'best_test_error': 100, 'clock': time.clock()}
    def on_epoch_done(epoch, n, o, loss, acc, valid_loss, valid_acc, test_loss, test_acc):
        error = 100 * (1 - acc)
        valid_error = 100 * (1 - valid_acc)
        test_error = 100 * (1 - test_acc)
        print('epoch {} done'.format(epoch))
        print('train loss: {} error: {}'.format(loss, error))
        print('valid loss: {} error: {}'.format(valid_loss, valid_error))
        print('test  loss: {} error: {}'.format(test_loss, test_error))
        if valid_error < state['best_valid_error']:
            serializers.save_npz('{}.model'.format(model_prefix), n)
            serializers.save_npz('{}.state'.format(model_prefix), o)
            state['best_valid_error'] = valid_error
            state['best_test_error'] = test_error
        if args.save_iter > 0 and (epoch + 1) % args.save_iter == 0:
            serializers.save_npz('{}_{}.model'.format(model_prefix, epoch + 1), n)
            serializers.save_npz('{}_{}.state'.format(model_prefix, epoch + 1), o)
        # prevent divergence when using identity mapping model
        if args.model == 'identity_mapping' and epoch < 9:
            o.lr = 0.01 + 0.01 * (epoch + 1)
#        if len(lr_decay_iter) == 1 and (epoch + 1) % lr_decay_iter[0] == 0 or epoch + 1 in lr_decay_iter:
        # Note, "lr_decay_iter" should be a list object to store a training schedule,
        # However, to keep up with the Python3.5, I changed to an integer value...
        if (epoch + 1) % args.lr_decay_iter == 0 and epoch > 1:
            if hasattr(optimizer, 'alpha'):
                o.alpha *= 0.1
            else:
                o.lr *= 0.1
        clock = time.clock()
        print('elapsed time: {}'.format(clock - state['clock']))
        state['clock'] = clock
        
        with open(log_file_path, 'a') as f:
            f.write('{},{},{},{},{},{},{}\n'.format(epoch + 1, loss, error, valid_loss, valid_error, test_loss, test_error))

    if args.resume == 'no':
        print(" Create %s as a New Logfile" % log_file_path)
        with open(log_file_path, 'w') as f:
            f.write('epoch,train loss,train acc,valid loss,valid acc,test loss,test acc\n')
    else:
        print(" Overwrite Existing Logfile %s" % log_file_path)

    cifar_trainer.fit(train_x, train_y, valid_x, valid_y, args.siz, args.dim, test_x, test_y, on_epoch_done)

    print('best test error: {}'.format(state['best_test_error']))

    with open("train_status.txt", 'w') as f:
        f.write("stop")

# -----------------------------------------------------------------------
# END OF PROGRAM
# -----------------------------------------------------------------------
