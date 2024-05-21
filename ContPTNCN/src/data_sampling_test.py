from utils_u.seq_sampler_2d import DataLoader2D

dl = DataLoader2D("max_improv_data.txt", 1)

# for elem in dl:
#     print("\n___\n")
#     for item in elem[0]:
#         print(f"items: L-{item[0]}, R-{item[1]}")
