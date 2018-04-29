if [ -z "$1" ];
then
    python sample.py \
        --init_dir=drake_output_hidden256_layers1_batch64 \
        --start_text="The meaning of life" \
        --length=100
else
    python sample.py \
        --init_dir=drake_output_hidden256_layers1_batch64 \
        --start_text="$1" \
        --length=100
fi
