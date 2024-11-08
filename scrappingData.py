import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import re
import time
import os
from urllib.parse import urljoin

class Rumah123Scraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.base_url = "https://www.rumah123.com/jual/yogyakarta/rumah/"
        self.image_folder = "property_images"
        if not os.path.exists(self.image_folder):
            os.makedirs(self.image_folder)

    def download_image(self, image_url, image_name):
        """Download dan simpan gambar"""
        try:
            response = requests.get(image_url, headers=self.headers)
            if response.status_code == 200:
                image_path = os.path.join(self.image_folder, f"{image_name}.jpg")
                with open(image_path, 'wb') as f:
                    f.write(response.content)
                return image_path
            return None
        except Exception as e:
            print(f"Error downloading image: {e}")
            return None

    def extract_price(self, text):
        """Ekstrak harga dari string"""
        if not text:
            return None
        # Menghapus 'Rp' dan 'Juta', kemudian mengkonversi ke angka
        match = re.search(r'Rp\s*(\d+(?:\.\d+)?)\s*(?:Juta|Miliar)?', text)
        if match:
            number = float(match.group(1))
            if 'Miliar' in text:
                number *= 1000  # Konversi ke juta
            return number
        return None

    def parse_time_ago(self, time_str):
        """Mengkonversi string waktu relatif ke datetime"""
        if not time_str:
            return None
        
        time_str = time_str.lower()
        current_time = datetime.now()
        
        hours_match = re.search(r'(\d+)\s+jam', time_str)
        if hours_match:
            hours = int(hours_match.group(1))
            return current_time - timedelta(hours=hours)
            
        days_match = re.search(r'(\d+)\s+hari', time_str)
        if days_match:
            days = int(days_match.group(1))
            return current_time - timedelta(days=days)
            
        return None

    def extract_number(self, text):
        """Ekstrak angka dari string"""
        if not text:
            return None
        match = re.search(r'(\d+)', text)
        return int(match.group(1)) if match else None

    def extract_area(self, text):
        """Ekstrak luas dari string dengan format 'XX m²'"""
        if not text:
            return None
        match = re.search(r'(\d+)\s*m²', text)
        return int(match.group(1)) if match else None

    def scrape_property_card(self, card, index):
        """Ekstrak informasi dari satu card properti"""
        try:
            # Ekstrak judul dan link
            title_elem = card.find('h2')
            title = title_elem.text.strip() if title_elem else None
            link_elem = title_elem.find_parent('a') if title_elem else None
            link = urljoin('https://www.rumah123.com', link_elem['href']) if link_elem and 'href' in link_elem.attrs else None
            
            # Ekstrak gambar
            image_url = None
            image_path = None
            carousel = card.find('div', class_='ui-molecules-carousel__content')
            if carousel:
                img_tag = carousel.find('img')
                if img_tag and 'src' in img_tag.attrs:
                    image_url = img_tag['src']
                    if image_url.startswith('//'):
                        image_url = 'https:' + image_url
                    elif not image_url.startswith('http'):
                        image_url = urljoin('https://www.rumah123.com', image_url)
                    image_path = self.download_image(image_url, f"property_{index}")

            # Ekstrak harga
            price_elem = card.find('div', class_='card-featured__middle-section__price')
            price = self.extract_price(price_elem.text) if price_elem else None

            # Ekstrak lokasi
            location_elem = card.find('span', string=lambda text: text and ',' in text)
            location = location_elem.text.strip() if location_elem else None

            # Ekstrak atribut (kamar tidur, kamar mandi, parkir)
            attribute_list = card.find('div', class_='card-featured__middle-section__attribute')
            kamar_tidur = None
            kamar_mandi = None
            parkir = None
            luas_bangunan = None
            luas_tanah = None

            if attribute_list:
                # Ekstrak kamar tidur, kamar mandi, parkir
                for item in attribute_list.find_all('div', class_='ui-molecules-list__item'):
                    attribute_text = item.text.strip()
                    if item.find('use', attrs={'xlink:href': '#rui-icon-bed-small'}):
                        kamar_tidur = self.extract_number(attribute_text)
                    elif item.find('use', attrs={'xlink:href': '#rui-icon-bath-small'}):
                        kamar_mandi = self.extract_number(attribute_text)
                    elif item.find('use', attrs={'xlink:href': '#rui-icon-car-small'}):
                        parkir = self.extract_number(attribute_text)

                # Ekstrak luas tanah dan bangunan
                for info in attribute_list.find_all('div', class_='attribute-info'):
                    if 'LT:' in info.text:
                        luas_tanah = self.extract_area(info.text)
                    elif 'LB:' in info.text:
                        luas_bangunan = self.extract_area(info.text)

            # Ekstrak waktu update
            update_elem = card.find('p', string=lambda text: text and 'Diperbarui' in text)
            update_time = update_elem.text.strip() if update_elem else None
            timestamp = self.parse_time_ago(update_time)

            return {
                'id': index,
                'judul': title,
                'link': link,
                'harga': price,
                'lokasi': location,
                'image_url': image_url,
                'image_path': image_path,
                'kamar_tidur': kamar_tidur,
                'kamar_mandi': kamar_mandi,
                'parkir': parkir,
                'luas_bangunan': luas_bangunan,
                'luas_tanah': luas_tanah,
                'waktu_update': timestamp
            }
            
        except Exception as e:
            print(f"Error saat mengekstrak card: {e}")
            return None

    def scrape_page(self, page=1, start_index=0):
        """Scrape satu halaman listing properti"""
        url = f"{self.base_url}?page={page}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Cari semua card properti dengan kelas yang benar
            property_cards = soup.find_all('div', class_='featured-card-component')
            
            results = []
            for i, card in enumerate(property_cards, start=start_index):
                property_data = self.scrape_property_card(card, i)
                if property_data:
                    results.append(property_data)
            
            return results
            
        except Exception as e:
            print(f"Error saat scraping halaman {page}: {e}")
            return []

    def scrape_properties(self, num_pages=1):
        """Scrape multiple pages dan simpan hasilnya"""
        all_properties = []
        start_index = 0
        
        for page in range(1, num_pages + 1):
            print(f"Scraping halaman {page}...")
            properties = self.scrape_page(page, start_index)
            all_properties.extend(properties)
            start_index += len(properties)
            
            # Delay untuk menghindari rate limiting
            time.sleep(2)
        
        # Simpan ke DataFrame
        df = pd.DataFrame(all_properties)
        
        # Simpan ke CSV
        filename = f"properti_yogyakarta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        print(f"Data berhasil disimpan ke {filename}")
        
        return df

# Contoh penggunaan
if __name__ == "__main__":
    scraper = Rumah123Scraper()
    df = scraper.scrape_properties(num_pages=5)  # Scrape 5 halaman pertama
    print(f"Total properti yang berhasil di-scrape: {len(df)}")