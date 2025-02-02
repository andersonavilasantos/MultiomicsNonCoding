# Top 20 Configurations from BioDeepFuse experiments

python main.py --train /mnt/UFZ-Data/anderson/NAR-Data/train/ --test /mnt/UFZ-Data/anderson/NAR-Data/test/ --epochs 20 --patience 5 --encoding 1 --concat 1 --k 1 --feat_extraction 1 --features_exist 0 --num_convs 4 --activation 0 --batch_norm 1 --cnn_dropout 0.2 --num_lstm 0 --bidirectional 0 --lstm_dropout 0.2 --output results/enc1_cnn_4conv_k1_concat1_bio

python main.py --train /mnt/UFZ-Data/anderson/NAR-Data/train/ --test /mnt/UFZ-Data/anderson/NAR-Data/test/ --epochs 20 --patience 5 --encoding 1 --k 1 --features_exist 1 --num_convs 4 --activation 0 --batch_norm 1 --cnn_dropout 0.2 --num_lstm 0 --bidirectional 0 --lstm_dropout 0.2 --output results/enc1_cnn_4conv_k1

python main.py --train /mnt/UFZ-Data/anderson/NAR-Data/train/ --test /mnt/UFZ-Data/anderson/NAR-Data/test/ --epochs 20 --patience 5 --encoding 1 --concat 2 --k 1 --feat_extraction 1 --features_exist 1 --num_convs 3 --activation 0 --batch_norm 1 --cnn_dropout 0.2 --num_lstm 1 --bidirectional 1 --lstm_dropout 0.2 --output results/enc1_cnn_bilstm_3conv_k1_concat2_bio

python main.py --train /mnt/UFZ-Data/anderson/NAR-Data/train/ --test /mnt/UFZ-Data/anderson/NAR-Data/test/ --epochs 20 --patience 5 --encoding 1 --k 3 --features_exist 1 --num_convs 4 --activation 0 --batch_norm 1 --cnn_dropout 0.2 --num_lstm 0 --bidirectional 0 --lstm_dropout 0.2 --output results/enc1_cnn_4conv_k3

python main.py --train /mnt/UFZ-Data/anderson/NAR-Data/train/ --test /mnt/UFZ-Data/anderson/NAR-Data/test/ --epochs 20 --patience 5 --encoding 1 --concat 2 --k 2 --feat_extraction 1 --features_exist 1 --num_convs 3 --activation 0 --batch_norm 1 --cnn_dropout 0.2 --num_lstm 0 --bidirectional 0 --lstm_dropout 0.2 --output results/enc1_cnn_3conv_k2_concat2_bio

python main.py --train /mnt/UFZ-Data/anderson/NAR-Data/train/ --test /mnt/UFZ-Data/anderson/NAR-Data/test/ --epochs 20 --patience 5 --encoding 0 --concat 2 --k 1 --feat_extraction 1 --features_exist 1 --num_convs 4 --activation 0 --batch_norm 1 --cnn_dropout 0.2 --num_lstm 0 --bidirectional 0 --lstm_dropout 0.2 --output results/enc0_cnn_4conv_k1_concat2_bio

python main.py --train /mnt/UFZ-Data/anderson/NAR-Data/train/ --test /mnt/UFZ-Data/anderson/NAR-Data/test/ --epochs 20 --patience 5 --encoding 1 --concat 2 --k 1 --feat_extraction 1 --features_exist 1 --num_convs 3 --activation 0 --batch_norm 1 --cnn_dropout 0.2 --num_lstm 0 --bidirectional 0 --lstm_dropout 0.2 --output results/enc1_cnn_3conv_k1_concat2_bio

python main.py --train /mnt/UFZ-Data/anderson/NAR-Data/train/ --test /mnt/UFZ-Data/anderson/NAR-Data/test/ --epochs 20 --patience 5 --encoding 1 --concat 1 --k 1 --feat_extraction 1 --features_exist 1 --num_convs 3 --activation 0 --batch_norm 1 --cnn_dropout 0.2 --num_lstm 1 --bidirectional 1 --lstm_dropout 0.2 --output results/enc1_cnn_bilstm_3conv_k1_concat1_bio

python main.py --train /mnt/UFZ-Data/anderson/NAR-Data/train/ --test /mnt/UFZ-Data/anderson/NAR-Data/test/ --epochs 20 --patience 5 --encoding 3 --concat 2 --k 2 --feat_extraction 1 --features_exist 1 --num_convs 3 --activation 0 --batch_norm 1 --cnn_dropout 0.2 --num_lstm 0 --bidirectional 0 --lstm_dropout 0.2 --output results/enc2_cnn_3conv_k2_concat2_bio

python main.py --train /mnt/UFZ-Data/anderson/NAR-Data/train/ --test /mnt/UFZ-Data/anderson/NAR-Data/test/ --epochs 20 --patience 5 --encoding 1 --concat 2 --k 1 --feat_extraction 1 --features_exist 1 --num_convs 4 --activation 0 --batch_norm 1 --cnn_dropout 0.2 --num_lstm 1 --bidirectional 1 --lstm_dropout 0.2 --output results/enc1_cnn_bilstm_4conv_k1_concat2_bio

python main.py --train /mnt/UFZ-Data/anderson/NAR-Data/train/ --test /mnt/UFZ-Data/anderson/NAR-Data/test/ --epochs 20 --patience 5 --encoding 0 --concat 2 --k 1 --feat_extraction 1 --features_exist 1 --num_convs 4 --activation 0 --batch_norm 1 --cnn_dropout 0.2 --num_lstm 1 --bidirectional 1 --lstm_dropout 0.2 --output results/enc0_cnn_bilstm_4conv_k1_concat2_bio

python main.py --train /mnt/UFZ-Data/anderson/NAR-Data/train/ --test /mnt/UFZ-Data/anderson/NAR-Data/test/ --epochs 20 --patience 5 --encoding 3 --concat 2 --k 3 --feat_extraction 1 --features_exist 1 --num_convs 2 --activation 0 --batch_norm 1 --cnn_dropout 0.2 --num_lstm 1 --bidirectional 1 --lstm_dropout 0.2 --output results/enc2_cnn_bilstm_2conv_k3_concat2_bio

python main.py --train /mnt/UFZ-Data/anderson/NAR-Data/train/ --test /mnt/UFZ-Data/anderson/NAR-Data/test/ --epochs 20 --patience 5 --encoding 1 --concat 1 --k 1 --feat_extraction 1 --features_exist 1 --num_convs 4 --activation 0 --batch_norm 1 --cnn_dropout 0.2 --num_lstm 1 --bidirectional 1 --lstm_dropout 0.2 --output results/enc1_cnn_bilstm_4conv_k1_concat1_bio

python main.py --train /mnt/UFZ-Data/anderson/NAR-Data/train/ --test /mnt/UFZ-Data/anderson/NAR-Data/test/ --epochs 20 --patience 5 --encoding 3 --concat 1 --k 1 --feat_extraction 1 --features_exist 1 --num_convs 4 --activation 0 --batch_norm 1 --cnn_dropout 0.2 --num_lstm 1 --bidirectional 1 --lstm_dropout 0.2 --output results/enc2_cnn_bilstm_4conv_k1_concat1_bio

python main.py --train /mnt/UFZ-Data/anderson/NAR-Data/train/ --test /mnt/UFZ-Data/anderson/NAR-Data/test/ --epochs 20 --patience 5 --encoding 0 --k 1 --features_exist 1 --num_convs 4 --activation 0 --batch_norm 1 --cnn_dropout 0.2 --num_lstm 0 --bidirectional 0 --lstm_dropout 0.2 --output results/enc0_cnn_4conv_k1

python main.py --train /mnt/UFZ-Data/anderson/NAR-Data/train/ --test /mnt/UFZ-Data/anderson/NAR-Data/test/ --epochs 20 --patience 5 --encoding 0 --concat 1 --k 1 --feat_extraction 1 --features_exist 1 --num_convs 4 --activation 0 --batch_norm 1 --cnn_dropout 0.2 --num_lstm 1 --bidirectional 1 --lstm_dropout 0.2 --output results/enc0_cnn_bilstm_4conv_k1_concat1_bio

python main.py --train /mnt/UFZ-Data/anderson/NAR-Data/train/ --test /mnt/UFZ-Data/anderson/NAR-Data/test/ --epochs 20 --patience 5 --encoding 3 --concat 2 --k 1 --feat_extraction 1 --features_exist 1 --num_convs 2 --activation 0 --batch_norm 1 --cnn_dropout 0.2 --num_lstm 1 --bidirectional 1 --lstm_dropout 0.2 --output results/enc2_cnn_bilstm_2conv_k1_concat2_bio

python main.py --train /mnt/UFZ-Data/anderson/NAR-Data/train/ --test /mnt/UFZ-Data/anderson/NAR-Data/test/ --epochs 20 --patience 5 --encoding 3 --k 1 --features_exist 1 --num_convs 4 --activation 0 --batch_norm 1 --cnn_dropout 0.2 --num_lstm 1 --bidirectional 1 --lstm_dropout 0.2 --output results/enc2_cnn_bilstm_4conv_k1

python main.py --train /mnt/UFZ-Data/anderson/NAR-Data/train/ --test /mnt/UFZ-Data/anderson/NAR-Data/test/ --epochs 20 --patience 5 --encoding 3 --concat 2 --k 1 --feat_extraction 1 --features_exist 1 --num_convs 3 --activation 0 --batch_norm 1 --cnn_dropout 0.2 --num_lstm 0 --bidirectional 0 --lstm_dropout 0.2 --output results/enc2_cnn_3conv_k1_concat2_bio

python main.py --train /mnt/UFZ-Data/anderson/NAR-Data/train/ --test /mnt/UFZ-Data/anderson/NAR-Data/test/ --epochs 20 --patience 5 --encoding 3 --concat 2 --k 1 --feat_extraction 1 --features_exist 1 --num_convs 2 --activation 0 --batch_norm 1 --cnn_dropout 0.2 --num_lstm 0 --bidirectional 0 --lstm_dropout 0.2 --output results/enc2_cnn_2conv_k1_concat2_bio