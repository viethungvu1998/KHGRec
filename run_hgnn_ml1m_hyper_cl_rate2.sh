CUDA_VISIBLE_DEVICES=1 python main.py --model=HGNN --dataset=ml-1m --n_layers=2 --lrate=0.001 --weight_decay=5e-6 --drop_rate=0.3 --p=0.3 --cl_rate=0.001 --temp=0.1 --reg=0.1 --early_stopping_steps=50
CUDA_VISIBLE_DEVICES=1 python main.py --model=HGNN --dataset=ml-1m --n_layers=2 --lrate=0.001 --weight_decay=5e-6 --drop_rate=0.3 --p=0.3 --cl_rate=0.1 --temp=0.1 --reg=0.1 --early_stopping_steps=50