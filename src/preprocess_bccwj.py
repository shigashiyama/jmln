import argparse

from logzero import logger


def read_and_write(
        input_path: str,
        output_path: str,
        core_ids: set[str],
) -> None:

    cnt = 0
    words = []
    cur_doc_id = None
    idx_tok_b = -1 
    idx_tok_e = -1

    with (
            open(input_path, encoding='utf-8') as f,
            open(output_path, 'w', encoding='utf-8') as fw,
    ):
        logger.info(f'Read: {input_path}')
        for line in f:
            line        = line.rstrip('\n')
            array       = line.split('\t')
            doc_id      = array[1]
            tok_id      = array[4]
            bos_flag    = array[9]
            surf        = array[23]

            if bos_flag == 'B':
                if cnt > 0 and cnt % 100000 == 0:
                    logger.info(f'Read {cnt} sentences')

                if words:
                    if not cur_doc_id in core_ids:
                        sid = f'{cur_doc_id}:{idx_tok_b}-{idx_tok_e}'
                        sent = ''.join(words)
                        fw.write(f'{sid}\t{sent}\n')

                cnt += 1
                cur_doc_id = doc_id
                idx_tok_b = tok_id
                idx_tok_e = tok_id
                words = [surf]

            else:
                idx_tok_e = tok_id
                words.append(surf)

        if words and not cur_doc_id in core_ids:
            sid = f'{cur_doc_id}:{idx_tok_b}:{idx_tok_e}'
            sent = ''.join(words)
            fw.write(f'{sid}\t{sent}\n')

        logger.info(f'Saved: {output_path}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', '-i', type=str, required=True)
    parser.add_argument('--output_path', '-o', type=str, required=True)
    parser.add_argument('--core_id_file', '-c', type=str, required=True)
    args = parser.parse_args()

    core_ids = set()
    with open(args.core_id_file) as f:
        logger.info(f'Read: {args.core_id_file}')
        for line in f:
            if line.startswith('#'):
                continue

            cid  = line.rstrip('\n')
            core_ids.add(cid)
            
    read_and_write(args.input_path, args.output_path, core_ids)
