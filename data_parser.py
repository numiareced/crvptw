import re
import global_vars

file_header = {
    'default_name': 'R101',
    'header_mapping': {
        'XCOORD.': 'x',
        'YCOORD.': 'y',
        'DEMAND': 'demand',
        'READY TIME': 'ready_time',
        'DUE DATE': 'due_time',
        'SERVICE TIME': 'service_time',
    }
}

def read_data(case: str, data_start_row: int = 10) -> list:
    collected_data = []
    path = "data/"
    i = 0
    header_mapping = file_header['header_mapping'];
    with open(path + case + '.txt', 'r') as data_file:
        for line in data_file:
            i = i + 1
            if i ==5:
                str_split = line.split()
                max_vehicle_num = int(str_split[0])
                capacity = int(str_split[-1])
                global_vars.vehicle_capacity = capacity
                global_vars.max_vehicles_num = max_vehicle_num
            if i == 8:
                header_str = re.split(r'\s{3,}', line)
                stripped = header_str[-1].rstrip()
                header_str[-1] = stripped
                for head, mapped in header_mapping.items():
                    j = header_str.index(head)
                    header_str[j] = mapped
            if i > data_start_row:
                str_line = line.split()
                collected_data.append({header_str[j]: value for j, value in enumerate(str_line)})
    return collected_data


def write_output(name: str, route_list: list):
    outfile = 'output/' + name + '.sol'
    with open(outfile, 'w+') as file:
        file.writelines(' '.join(str(j) for j in i) + '\n' for i in route_list)


