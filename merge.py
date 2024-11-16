import pandas as pd
import os
import glob

def merge_csv_files(input_path, output_file):
    """
    Menggabungkan semua file CSV dalam sebuah direktori menjadi satu file CSV.
    
    Parameters:
    input_path (str): Path ke direktori yang berisi file CSV
    output_file (str): Nama file output untuk hasil penggabungan
    """
    
    # Mendapatkan semua file CSV dalam direktori
    all_files = glob.glob(os.path.join(input_path, "*.csv"))
    
    if not all_files:
        print(f"Tidak ada file CSV yang ditemukan di {input_path}")
        return
    
    print(f"Ditemukan {len(all_files)} file CSV:")
    for file in all_files:
        print(f"- {os.path.basename(file)}")
    
    # List untuk menyimpan semua DataFrame
    df_list = []
    
    # Membaca setiap file CSV
    for file in all_files:
        try:
            df = pd.read_csv(file)
            df_list.append(df)
            print(f"Berhasil membaca: {os.path.basename(file)} ({len(df)} baris)")
        except Exception as e:
            print(f"Error membaca {os.path.basename(file)}: {str(e)}")
    
    if not df_list:
        print("Tidak ada data yang bisa digabungkan")
        return
    
    # Menggabungkan semua DataFrame
    combined_df = pd.concat(df_list, ignore_index=True)
    
    # Menyimpan hasil ke file baru
    try:
        combined_df.to_csv(output_file, index=False)
        print(f"\nPenggabungan berhasil!")
        print(f"Total baris: {len(combined_df)}")
        print(f"File hasil penggabungan: {output_file}")
    except Exception as e:
        print(f"Error menyimpan file: {str(e)}")

# Contoh penggunaan
if __name__ == "__main__":
    # Ganti dengan path direktori yang berisi file CSV Anda
    input_directory = "data"
    
    # Ganti dengan nama file output yang diinginkan
    output_filename = "combined_output.csv"
    
    merge_csv_files(input_directory, output_filename)