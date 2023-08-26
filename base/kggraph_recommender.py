import time
from time import strftime, localtime
import os 
import pandas as pd 
from os.path import abspath
import sys
import csv 
import torch
import torch.nn as nn 
import torch.nn.functional as F

from base.recommender import Recommender
from util.algorithm import find_k_largest
from data.loader import FileIO
from util.evaluation import ranking_evaluation
from data.ui_graph import InteractionKG
from data.knowledge import Knowledge 

class KGGraphRecommender(Recommender):
    def __init__(self, conf, training_set, test_set, knowledge_set, **kwargs):
        super(KGGraphRecommender, self).__init__(conf, training_set, test_set, knowledge_set,**kwargs)        
        self.data = InteractionKG(conf, training_set, test_set)
        self.data_kg = Knowledge(conf, training_set, test_set, knowledge_set)

        self.bestPerformance = []
        top = self.ranking['-topN'].split(',')
        self.topN = [int(num) for num in top]
        self.max_N = max(self.topN)
        
        self.output_path =  f"./results/{kwargs['model']}/{kwargs['dataset']}/@KGAT-inp_emb:{kwargs['input_dim']}-emb:{kwargs['embedding_size']}-bs:{kwargs['batch_size']}-lr:{kwargs['lrate']}-lr_kg:{kwargs['lratekg']}-n_layers:{kwargs['n_layers']}/"
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
            
    def print_model_info(self):
        super(KGGraphRecommender, self).print_model_info()
        # # print dataset statistics
        print('Training Set Size: (user number: %d, item number %d, interaction number: %d)' % (self.data.training_size()))
        print('Test Set Size: (user number: %d, item number %d, interaction number: %d)' % (self.data.test_size()))
        print('=' * 80)

    def build(self):
        pass

    def train(self):
        pass

    def predict(self, u):
        pass

    def test(self, user_emb, item_emb):
        def process_bar(num, total):
            rate = float(num) / total
            ratenum = int(50 * rate)
            r = '\rProgress: [{}{}]{}%'.format('+' * ratenum, ' ' * (50 - ratenum), ratenum*2)
            sys.stdout.write(r)
            sys.stdout.flush()
        # predict
        rec_list = {}
        user_count = len(self.data.test_set)
        lst_users =  list(self.data_kg.userent.keys())
        lst_items =  list(self.data_kg.itement.keys())
        for i, user in enumerate(self.data.test_set):
            user_id  = lst_users.index(user)
            score = torch.matmul(user_emb[user_id], item_emb.transpose(0, 1))
            candidates = score.cpu().numpy()
            
            rated_list, li = self.data.user_rated(user)
            for item in rated_list:
                candidates[lst_items.index(item)] = -10e8
            # s_find_k_largest = time.time()
            ids, scores = find_k_largest(self.max_N, candidates)
            # e_find_k_largest = time.time()
            # print("Find k largest candidates: %f s" % (e_find_k_largest - s_find_k_largest))
            item_names = [lst_items[iid] for iid in ids]
            rec_list[user] = list(zip(item_names, scores))
            if i % 1000 == 0:
                process_bar(i, user_count)
        process_bar(user_count, user_count)
        print('')
        return rec_list
    
    def evaluate(self, rec_list):
        self.recOutput.append('userId: recommendations in (itemId, ranking score) pairs, * means the item is hit.\n')
        for user in self.data.test_set:
            line = str(user) + ':'
            for item in rec_list[user]:
                line += ' (' + str(item[0]) + ',' + str(item[1]) + ')'
                if item[0] in self.data.test_set[user]:
                    line += '*'
            line += '\n'
            self.recOutput.append(line)
        current_time = strftime("%Y-%m-%d %H-%M-%S", localtime(time.time()))
        # output prediction result
        out_dir = self.output_path
        file_name = self.config['model.name'] + '@' + current_time + '-top-' + str(self.max_N) + 'items' + '.txt'
        FileIO.write_file(out_dir, file_name, self.recOutput)
        print('The result has been output to ', abspath(out_dir), '.')
        file_name = self.config['model.name'] + '@' + current_time + '-performance' + '.txt'
        self.result = ranking_evaluation(self.data.test_set, rec_list, self.topN)
        self.model_log.add('###Evaluation Results###')
        self.model_log.add(self.result)
        FileIO.write_file(out_dir, file_name, self.result)
        print('The result of %s:\n%s' % (self.model_name, ''.join(self.result)))

    def fast_evaluation(self, model, epoch, user_embed, item_embed, kwargs=None):
        print('Evaluating the model...')
        s_test = time.time()
        rec_list = test(self.data, self.data_kg, user_embed, item_embed, self.max_N)
        e_test = time.time() 
        print("Test time: %f s" % (e_test - s_test))
        
        s_measure = time.time()
        measure = ranking_evaluation(self.data.test_set, rec_list, [self.max_N])
        e_measure = time.time()
        print("Measure time: %f s" % (e_measure - s_measure))
        
        if len(self.bestPerformance) > 0:
            count = 0
            performance = {}
            for m in measure[1:]:
                k, v = m.strip().split(':')
                performance[k] = float(v)
            for k in self.bestPerformance[1]:
                if self.bestPerformance[1][k] > performance[k]:
                    count += 1
                else:
                    count -= 1
            if count < 0:
                self.bestPerformance[1] = performance
                self.bestPerformance[0] = epoch + 1
                # try:
                #     self.save(kwargs)
                # except:
                self.save(model)
        else:
            self.bestPerformance.append(epoch + 1)
            performance = {}
            for m in measure[1:]:
                k, v = m.strip().split(':')
                performance[k] = float(v)
            self.bestPerformance.append(performance)
            # try:
            #     self.save(kwargs)
            # except:
            self.save(model)
        print('-' * 120)
        print('Real-Time Ranking Performance ' + ' (Top-' + str(self.max_N) + ' Item Recommendation)')
        measure = [m.strip() for m in measure[1:]]
        print('*Current Performance*')
        print('Epoch:', str(epoch + 1) + ',', '  |  '.join(measure))
        bp = ''
        # for k in self.bestPerformance[1]:
        #     bp+=k+':'+str(self.bestPerformance[1][k])+' | '
        bp += 'Hit Ratio' + ':' + str(self.bestPerformance[1]['Hit Ratio']) + '  |  '
        bp += 'Precision' + ':' + str(self.bestPerformance[1]['Precision']) + '  |  '
        bp += 'Recall' + ':' + str(self.bestPerformance[1]['Recall']) + '  |  '
        # bp += 'F1' + ':' + str(self.bestPerformance[1]['F1']) + ' | '
        bp += 'NDCG' + ':' + str(self.bestPerformance[1]['NDCG'])
        print('*Best Performance* ')
        print('Epoch:fast_evaluation', str(self.bestPerformance[0]) + ',', bp)
        print('-' * 120)
        return measure
    
    def save(self, model):
        with torch.no_grad():
            ego_emb =  model.calc_cf_embeddings()
            user_emb = ego_emb[model.user_indices]
            item_emb = ego_emb[model.item_indices]
            self.best_user_emb, self.best_item_emb = user_emb, item_emb
        self.save_model(model)
    
    def save_model(self, model):
        # save model 
        current_time = strftime("%Y-%m-%d", localtime(time.time()))
        out_dir = self.output_path
        file_name =  self.config['model.name'] + '@' + current_time + '-weight' + '.pth'
        weight_file = out_dir + '/' + file_name 
        torch.save(model.state_dict(), weight_file)

    def save_performance_row(self, ep, data_ep):
        # opening the csv file in 'w' mode
        csv_path = self.output_path + 'train_performance.csv'
        
        # 'Hit Ratio:0.00328', 'Precision:0.00202', 'Recall:0.00337', 'NDCG:0.00292
        hit = float(data_ep[0].split(':')[1])
        precision = float(data_ep[1].split(':')[1])
        recall = float(data_ep[2].split(':')[1])
        ndcg = float(data_ep[3].split(':')[1])
        
        with open(csv_path, 'a+', newline = '') as f:
            header = ['ep', 'hit@20', 'prec@20', 'recall@20', 'ndcg@20']
            writer = csv.DictWriter(f, fieldnames = header)
            # writer.writeheader()
            writer.writerow({
                 'ep' : ep,
                 'hit@20': hit,
                 'prec@20': precision,
                 'recall@20': recall,
                 'ndcg@20': ndcg,
            })
            
    def save_loss_row(self, data_ep):
        csv_path = self.output_path + 'loss.csv'
        with open(csv_path, 'a+', newline ='') as f:
            header = ['ep', 'train_loss', 'cf_loss', 'kg_loss']
            writer = csv.DictWriter(f, fieldnames = header)
            # writer.writeheader()
            writer.writerow({
                'ep' : data_ep[0],
                'train_loss': data_ep[1],
                 'cf_loss': data_ep[2],
                 'kg_loss': data_ep[3]
            })

    def save_loss(self, train_losses, rec_losses, kg_losses):
        df_train_loss = pd.DataFrame(train_losses, columns = ['ep', 'loss'])
        df_rec_loss = pd.DataFrame(rec_losses, columns = ['ep', 'loss'])
        df_kg_loss = pd.DataFrame(kg_losses, columns = ['ep', 'loss'])
        df_train_loss.to_csv(self.output_path + '/train_loss.csv')
        df_rec_loss.to_csv(self.output_path + '/rec_loss.csv')
        df_kg_loss.to_csv(self.output_path + '/kg_loss.csv')
    
    def save_perfomance_training(self, log_train):
        df_train_log = pd.DataFrame(log_train)
        df_train_log.to_csv(self.output_path + '/train_performance.csv')

def test(data, data_kg, user_emb, item_emb, max_N):
    def process_bar(num, total):
        rate = float(num) / total
        ratenum = int(50 * rate)
        r = '\rProgress: [{}{}]{}%'.format('+' * ratenum, ' ' * (50 - ratenum), ratenum*2)
        sys.stdout.write(r)
        sys.stdout.flush()
    # predict
    rec_list = {}
    user_count = len(data.test_set)
    lst_users =  list(data_kg.userent.keys())
    lst_items =  list(data_kg.itement.keys())
    for i, user in enumerate(data.test_set):
        user_id  = lst_users.index(user)
        score = torch.matmul(user_emb[user_id], item_emb.transpose(0, 1))
        candidates = score.cpu().numpy()
        
        rated_list, li = data.user_rated(user)
        for item in rated_list:
            candidates[lst_items.index(item)] = -10e8
        # s_find_k_largest = time.time()
        ids, scores = find_k_largest(max_N, candidates)
        # e_find_k_largest = time.time()
        # print("Find k largest candidates: %f s" % (e_find_k_largest - s_find_k_largest))
        item_names = [lst_items[iid] for iid in ids]
        rec_list[user] = list(zip(item_names, scores))
        if i % 1000 == 0:
            process_bar(i, user_count)
    process_bar(user_count, user_count)
    print('')
    return rec_list

