CUDA_VISIBLE_DEVICES=1 python main.py --experiment=missing --missing_pct=10 --model=HGNN --dataset=ml-1m --lrate=0.0001 --n_layers=2 --p=0.3 --drop_rate=0.2 --reg=0.1 --weight_decay=5e-6 --cl_rate=0.0001 --temp=1 --early_stopping_steps=50 --max_epoch=500
CUDA_VISIBLE_DEVICES=1 python main.py --experiment=missing --missing_pct=20 --model=HGNN --dataset=ml-1m --lrate=0.0001 --n_layers=2 --p=0.3 --drop_rate=0.2 --reg=0.1 --weight_decay=5e-6 --cl_rate=0.0001 --temp=1 --early_stopping_steps=50 --max_epoch=500
CUDA_VISIBLE_DEVICES=1 python main.py --experiment=missing --missing_pct=30 --model=HGNN --dataset=ml-1m --lrate=0.0001 --n_layers=2 --p=0.3 --drop_rate=0.2 --reg=0.1 --weight_decay=5e-6 --cl_rate=0.0001 --temp=1 --early_stopping_steps=50 --max_epoch=500
CUDA_VISIBLE_DEVICES=1 python main.py --experiment=missing --missing_pct=40 --model=HGNN --dataset=ml-1m --lrate=0.0001 --n_layers=2 --p=0.3 --drop_rate=0.2 --reg=0.1 --weight_decay=5e-6 --cl_rate=0.0001 --temp=1 --early_stopping_steps=50 --max_epoch=500
CUDA_VISIBLE_DEVICES=1 python main.py --experiment=missing --missing_pct=50 --model=HGNN --dataset=ml-1m --lrate=0.0001 --n_layers=2 --p=0.3 --drop_rate=0.2 --reg=0.1 --weight_decay=5e-6 --cl_rate=0.0001 --temp=1 --early_stopping_steps=50 --max_epoch=500