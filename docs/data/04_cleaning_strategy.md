# Data Cleaning & Standardization Strategy

## Document Metadata

| Field          | Value                                             |
| -------------- | ------------------------------------------------- |
| Document Title | Data Cleaning & Standardization Strategy          |
| Project        | Enterprise E-Commerce Analytics                   |
| Document Owner | Tulus Prapto                                      |
| Phase          | Sprint 3.1                                        |
| Source Layer   | `data/raw/`                                       |
| Previous Phase | Sprint 2 — Data Profiling & Relationship Analysis |
| Target Layer   | Clean Analytical Data                             |
| Primary Tools  | Python, Polars, Parquet, DuckDB                   |
| Status         | Approved for Implementation                       |

---

# 1. Purpose

Dokumen ini mendefinisikan strategi, aturan, dan prinsip yang digunakan untuk melakukan data cleaning dan standardization pada project Enterprise E-Commerce Analytics.

Tujuan utamanya adalah menghasilkan data yang:

* konsisten secara struktur;
* memiliki data type yang sesuai;
* mempertahankan informasi bisnis yang valid;
* dapat digunakan untuk analytical processing;
* dapat disimpan dalam format Parquet;
* dapat dimuat dan dianalisis menggunakan DuckDB;
* dapat ditelusuri kembali ke raw data;
* dapat divalidasi secara reproducible.

Raw data tidak akan dimodifikasi secara langsung.

---

# 2. Cleaning Principles

## 2.1 Raw Data Preservation

Dataset pada:

```text
data/raw/
```

merupakan immutable source layer.

Pipeline cleaning hanya membaca raw data dan menghasilkan output baru.

Tidak diperbolehkan melakukan overwrite terhadap raw dataset.

---

## 2.2 Business Meaning Over Mechanical Cleaning

Nilai NULL, duplicate, orphan record, dan unmatched record tidak otomatis dianggap sebagai kesalahan.

Setiap perubahan harus memiliki alasan teknis atau business rule yang jelas.

---

## 2.3 No Invented Data

Pipeline tidak boleh mengarang:

* nilai numerik;
* tanggal;
* kategori;
* geographic information;
* review;
* translation;
* customer information;
* seller information.

Jika informasi tidak tersedia, nilai akan tetap NULL atau diberi status yang sesuai.

---

## 2.4 Reproducibility

Cleaning harus dilakukan melalui script Python/Polars yang dapat dijalankan ulang.

Manual modification terhadap dataset hasil cleaning tidak diperbolehkan.

---

# 3. Target Data Layers

Pipeline menggunakan struktur berikut:

```text
RAW CSV
   │
   ▼
POLARS CLEANING
   │
   ▼
CLEAN DATA
   │
   ▼
PARQUET
   │
   ▼
DUCKDB
   │
   ▼
ANALYTICAL DATA MART
```

Setiap layer memiliki tujuan berbeda.

| Layer     | Purpose                             |
| --------- | ----------------------------------- |
| Raw       | Original source data                |
| Clean     | Standardized and validated data     |
| Parquet   | Efficient analytical storage        |
| DuckDB    | Analytical query layer              |
| Data Mart | Business-oriented analytical tables |

---

# 4. Data Type Standardization

## 4.1 Datetime Columns

Kolom berikut pada `olist_orders_dataset.csv` akan dikonversi dari String menjadi Datetime:

* `order_purchase_timestamp`
* `order_approved_at`
* `order_delivered_carrier_date`
* `order_delivered_customer_date`
* `order_estimated_delivery_date`

Kolom datetime harus menggunakan format yang konsisten.

NULL tetap dipertahankan.

---

## 4.2 Numeric Columns

Kolom numerik harus menggunakan numeric data types yang sesuai.

Contoh:

* `price`
* `freight_value`
* `payment_value`
* `review_score`
* product dimensions
* ZIP code prefixes

Nilai numerik tidak akan diubah hanya karena dianggap sebagai outlier tanpa business justification.

---

## 4.3 Identifier Columns

Identifier seperti:

* `order_id`
* `customer_id`
* `customer_unique_id`
* `product_id`
* `seller_id`

dipertahankan sebagai String.

Identifier tidak boleh dikonversi menjadi numeric type hanya karena memiliki format alfanumerik tertentu.

---

# 5. Missing Value Strategy

Missing values akan diperlakukan berdasarkan konteks bisnis.

## 5.1 Order Dates

NULL pada:

* `order_approved_at`
* `order_delivered_carrier_date`
* `order_delivered_customer_date`

tidak akan diimputasi secara otomatis.

NULL dapat merepresentasikan lifecycle order yang belum mencapai tahap tertentu atau kondisi order tertentu.

---

## 5.2 Product Attributes

NULL pada atribut produk seperti:

* `product_category_name`
* `product_name_lenght`
* `product_description_lenght`
* `product_photos_qty`
* `product_weight_g`
* `product_length_cm`
* `product_height_cm`
* `product_width_cm`

dipertahankan apabila tidak terdapat business rule yang valid untuk imputasi.

---

## 5.3 Review Content

NULL pada:

* `review_comment_title`
* `review_comment_message`

dipertahankan.

Tidak ada text review yang akan dibuat secara artifisial.

---

# 6. Duplicate Strategy

## 6.1 General Rule

Duplicate handling harus mempertimbangkan grain dataset.

Tidak semua repeated values merupakan duplicate rows.

---

## 6.2 Geolocation Dataset

`olist_geolocation_dataset.csv` memiliki lebih dari satu juta rows dan ditemukan duplicate rows dalam profiling.

Duplicate tidak akan langsung dihapus dari raw data.

Alasannya:

* ZIP prefix dapat memiliki beberapa geographic observations;
* latitude dan longitude dapat berbeda;
* city/state dapat memberikan konteks tambahan.

Deduplication hanya boleh dilakukan pada analytical lookup layer apabila diperlukan.

---

# 7. Category Translation Strategy

Dataset:

```text
product_category_name_translation.csv
```

digunakan sebagai mapping dari Portuguese category name ke English category name.

Dua kategori ditemukan tidak memiliki translation:

* `pc_gamer`
* `portateis_cozinha_e_preparadores_de_alimentos`

Kategori tersebut tidak akan diberikan translation buatan.

Nilai English category akan tetap NULL untuk kategori yang tidak memiliki mapping.

---

# 8. Referential Integrity Strategy

Hasil relationship analysis menunjukkan beberapa relationship penting.

## 8.1 Orders → Order Items

Ditemukan:

```text
775 orders without items
```

Record tersebut tidak akan otomatis dihapus.

Hasil deep validation menunjukkan sebagian besar terkait dengan order status seperti:

* `unavailable`
* `canceled`
* `created`
* `invoiced`
* `shipped`

Order tetap dipertahankan pada order-level dataset.

---

## 8.2 Orders → Payments

Ditemukan:

```text
1 order without payment
```

Record tidak akan dihapus.

Status order akan tetap digunakan sebagai business context.

---

## 8.3 Orders → Reviews

Ditemukan:

```text
768 orders without reviews
```

Order tetap dipertahankan.

Tidak memiliki review bukan merupakan alasan untuk menghapus order.

---

# 9. Geographic Data Strategy

Relationship analysis menemukan unmatched ZIP prefixes pada customer dan seller geolocation.

## Customer

```text
157 unmatched ZIP prefixes
278 affected customer rows
```

## Seller

```text
7 unmatched ZIP prefixes
7 affected seller rows
```

Unmatched geographic records tidak akan diimputasi menggunakan data eksternal pada cleaning phase.

Jika geographic enrichment diperlukan pada tahap lanjutan, proses tersebut harus didokumentasikan sebagai enrichment terpisah.

---

# 10. Outlier Strategy

Outlier detection yang dihasilkan pada profiling digunakan sebagai diagnostic signal.

Outlier tidak otomatis dihapus.

Contoh:

```text
price
freight_value
payment_value
```

Nilai ekstrem dapat merupakan transaksi valid.

Removal atau transformation hanya dapat dilakukan jika terdapat business rule yang mendukung.

---

# 11. Text Standardization

Text categorical fields dapat dinormalisasi secara aman melalui:

* trimming whitespace;
* standardisasi missing representation;
* konsistensi null handling.

Namun nilai kategori asli tidak boleh diubah secara semantik tanpa mapping yang terdokumentasi.

---

# 12. Data Quality Rules

Cleaned datasets harus memenuhi minimal rules berikut:

### Schema

* expected columns tersedia;
* data types sesuai;
* identifier tidak berubah;
* raw row-level information tidak hilang tanpa alasan terdokumentasi.

### Missing Values

* missing values terdokumentasi;
* tidak ada blanket imputation.

### Referential Integrity

* foreign key violations terukur;
* orphan records tidak dihapus secara otomatis.

### Numeric

* numeric fields dapat diproses secara numerik;
* negative values diperiksa;
* potential outliers dilaporkan.

### Datetime

* datetime dapat diparse;
* invalid datetime values harus dilaporkan;
* NULL datetime dipertahankan apabila valid secara bisnis.

---

# 13. Output Requirements

Cleaning pipeline harus menghasilkan:

```text
data/processed/
```

dengan format Parquet.

Setiap dataset hasil cleaning harus memiliki:

* consistent schema;
* standardized data types;
* deterministic transformation;
* documented row count;
* documented null count;
* documented validation status.

---

# 14. Cleaning Lineage

Setiap output harus dapat ditelusuri:

```text
data/raw/<dataset>.csv
        │
        ▼
src/cleaning/<pipeline>.py
        │
        ▼
data/processed/<dataset>.parquet
        │
        ▼
database/ecommerce.duckdb
```

Cleaning summary dan validation results akan disimpan pada:

```text
reports/cleaning/
```

---

# 15. Non-Goals

Sprint 3 cleaning tidak mencakup:

* predictive modeling;
* customer segmentation;
* machine learning;
* external geographic enrichment;
* revenue forecasting;
* recommendation engine;
* advanced business analytics.

Aktivitas tersebut dilakukan pada fase analisis berikutnya.

---

# 16. Acceptance Criteria

Sprint 3 cleaning implementation dianggap berhasil apabila:

1. Raw data tidak berubah.
2. Semua target dataset dapat diproses tanpa error.
3. Data types telah distandardisasi.
4. Datetime columns berhasil dikonversi.
5. Missing values ditangani sesuai business rules.
6. Duplicate handling mengikuti dataset grain.
7. Referential integrity tetap dapat diukur.
8. Unmatched geographic records tidak dihapus secara sembarangan.
9. Untranslated categories tidak diisi secara artifisial.
10. Clean datasets berhasil ditulis sebagai Parquet.
11. Parquet files dapat dibaca kembali menggunakan Polars.
12. Parquet files dapat dibaca menggunakan DuckDB.
13. Validation report berhasil dibuat.
14. Semua transformasi dapat direproduksi.
15. Semua artefak tercatat dalam Git.

---

# 17. Approval

Dokumen ini menjadi baseline untuk implementasi Sprint 3.

Setelah dokumen ini di-commit, perubahan terhadap cleaning rules harus melalui decision log dan tidak boleh dilakukan secara informal di dalam script.

**Status: Ready for Implementation**
