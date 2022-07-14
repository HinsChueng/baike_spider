import pandas

from common.log import get_logger

logger = get_logger(__name__)


def write_to_excel(file_path, header, data_list):
    with pandas.ExcelWriter(file_path, mode='w+') as writer:
        df = pandas.DataFrame(data_list)
        df.to_excel(writer, index=False, header=header)
        logger.info(f'写入成功：{file_path}')


def write_to_file(file_path, data: str):
    with open(file_path, 'w') as f:
        f.write(data)
        logger.info(f'写入成功：{file_path}')


def dict_to_list(keyword, **kwargs):
    write_list = []
    header = ['中文名称']
    row_count = 0

    for _, data in kwargs.items():
        for h2, h2_data in data.items():
            row_count = 1 if row_count <= 1 else row_count
            if not h2_data:
                write_list.append([keyword, h2])
            else:
                for h3, h3_data in h2_data.items():
                    row_count = 2 if row_count <= 2 else row_count
                    if not h3_data:
                        write_list.append([keyword, h2, h3])
                    else:
                        for h4, h4_data in h3_data.items():
                            row_count = 3 if row_count <= 3 else row_count
                            if not h4_data:
                                write_list.append([keyword, h2, h3, h4])
                            else:
                                for h5, _ in h4_data.items():
                                    row_count = 4 if row_count <= 4 else row_count
                                    write_list.append([keyword, h2, h3, h4, h5])

    header.extend(['' for _ in range(row_count)])

    return header, write_list
