import pandas as pd

def isi_parkir_kendaraan(df):
    # Fungsi untuk mengkonversi string harga ke nilai numerik (dalam jutaan)
    def ekstrak_harga(harga):
        try:
            # Jika input sudah berupa float, kembalikan langsung
            if isinstance(harga, (int, float)):
                return float(harga)
            
            # Jika input berupa string
            harga_str = str(harga)
            # Menghapus 'Rp' dan 'Jut'/'Mili'
            harga_str = harga_str.replace('Rp', '').strip()
            # Ganti koma dengan titik untuk angka desimal
            harga_str = harga_str.replace(',', '.')
            
            if 'Mili' in harga_str:
                # Konversi Miliar ke Juta
                nilai = float(harga_str.split('Mili')[0].strip()) * 1000
            else:
                # Ambil nilai Juta
                nilai = float(harga_str.split('Jut')[0].strip())
            return nilai
        except Exception as e:
            print(f"Error processing value: {harga} - Error: {str(e)}")
            return None

    # Konversi kolom harga ke nilai numerik
    df['harga_numerik'] = df['Harga'].apply(ekstrak_harga)
    
    # Fungsi untuk menentukan jumlah parkir berdasarkan harga
    def tentukan_parkir(row):
        if pd.isna(row['Parkir']):  # Hanya isi jika kosong
            if pd.isna(row['harga_numerik']):  # Jika harga tidak bisa diproses
                return 1
            elif row['harga_numerik'] >= 4000:  # 4 miliar
                return 3
            elif row['harga_numerik'] >= 1500:  # 1.5 miliar
                return 2
            else:
                return 1
        return row['Parkir']  # Kembalikan nilai yang sudah ada jika tidak kosong
    
    # Terapkan fungsi ke dataframe
    df['Parkir'] = df.apply(tentukan_parkir, axis=1)
    
    # Hapus kolom bantuan
    df = df.drop('harga_numerik', axis=1)
    
    return df

# Membaca file
input_file = 'data/Merged.csv'  # Ganti dengan nama file input Anda
output_file = 'data/Merged_V2.csv'  # Ganti dengan nama file output yang diinginkan

# Membaca data
df = pd.read_csv(input_file)

# Cetak beberapa baris pertama untuk debugging
print("Sample data:")
print(df[['Judul', 'Harga', 'Parkir']].head())
print("\nTipe data kolom Harga:", df['Harga'].dtype)

# Mengisi parkir kendaraan
df = isi_parkir_kendaraan(df)

# Menyimpan hasil ke file baru
df.to_csv(output_file, index=False)

print(f"\nFile telah diproses dan disimpan ke {output_file}")