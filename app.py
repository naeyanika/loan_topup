import streamlit as st
import pandas as pd
import numpy as np
import io
from datetime import datetime

st.title('Aplikasi Analisa Loan Top Up')
st.markdown("""
## File yang dibutuhkan
1. **LoanTopUp_Report.xlsx**
    - Data yang di perlukan sesuai periode audit!
    - Rapihkan data terlebih dahulu, seperti ini ( https://www.canva.com/design/DAGWIkt0l-c/dViHAgm-S3tCGKDpunRUcw/edit )
    - Hapus beberapa kolom yang tidak diperlukang (Biasanya ada kolom kosong di beberapa kolom yang ada)
    """)

## FUNGSI FORMAT NOMOR
def format_no(no):
    try:
        if pd.notna(no):
            return f'{int(no):02d}.'
        else:
            return ''
    except (ValueError, TypeError):
        return str(no)

def format_center(center):
    try:
        if pd.notna(center):
            return f'{int(center):03d}'
        else:
            return ''
    except (ValueError, TypeError):
        return str(center)

def format_kelompok(kelompok):
    try:
        if pd.notna(kelompok):
            return f'{int(kelompok):02d}'
        else:
            return ''
    except (ValueError, TypeError):
        return str(kelompok)

# Fungsi untuk format tanggal
def format_date(date):
    try:
        if pd.isna(date):
            return ''
        if isinstance(date, str):
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d-%m-%Y']:
                try:
                    date = datetime.strptime(date, fmt)
                    break
                except ValueError:
                    continue
        if isinstance(date, datetime):
            return date.strftime('%d-%m-%Y')
        return date
    except Exception:
        return date

# Fungsi untuk menghitung kolom validasi
def calculate_validation(row):
    if row['JENIS TOP UP'] == 'REGULER':
        if row['LOANAMOUNT'] > row['OUTSTANDING PINJAMAN LAMA'] or row['LOANAMOUNT'] < (0.5 * row['OUTSTANDING PINJAMAN LAMA']):
            return 'FALSE'
    return 'TRUE'

uploaded_file = st.file_uploader("Unggah file Excel", type=["xlsx"])

if uploaded_file is not None:
    # Membaca file Excel
    df1 = pd.read_excel(uploaded_file, engine='openpyxl')
    
    # Format kolom tanggal
    date_columns = ['TGL CAIR PINJAMAN LAMA', 'TGL CAIR', 'LAPORAN SD TANGGAL']
    for col in date_columns:
        if col in df1.columns:
            df1[col] = df1[col].apply(format_date)
    
    # Menambahkan kolom validasi
    df1['VALIDASI'] = df1.apply(calculate_validation, axis=1)
    
    # Filter Section
    st.subheader('Filter Data')
    
    # Buat dua kolom untuk filter
    col1, col2 = st.columns(2)
    
    with col1:
        # Filter BRANCHNAME
        all_branches = ['Semua'] + sorted(df1['BRANCHNAME'].unique().tolist())
        selected_branch = st.selectbox('Pilih Branch:', all_branches)
    
    with col2:
        # Filter Validasi
        validation_filter = st.radio(
            "Pilih Status Validasi:",
            ('Semua', 'TRUE', 'FALSE'),
            horizontal=True  # Membuat radio button horizontal
        )
    
    # Aplikasikan filter
    if selected_branch != 'Semua':
        filtered_df = df1[df1['BRANCHNAME'] == selected_branch]
    else:
        filtered_df = df1
        
    if validation_filter != 'Semua':
        filtered_df = filtered_df[filtered_df['VALIDASI'] == validation_filter]
    
    # Menampilkan informasi filter yang aktif
    st.markdown('---')  # Garis pemisah
    
    # Menampilkan jumlah data dalam box
    st.metric("Jumlah Data", len(filtered_df))
    
    # Menampilkan DataFrame yang sudah difilter
    st.dataframe(filtered_df)
    
    # Menambahkan tombol download untuk hasil filter
    def convert_df_to_excel():
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            filtered_df.to_excel(writer, index=False)
        return output.getvalue()
    
    excel_data = convert_df_to_excel()
    st.download_button(
        label="Download data terfilter sebagai Excel",
        data=excel_data,
        file_name='filtered_loan_topup.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
