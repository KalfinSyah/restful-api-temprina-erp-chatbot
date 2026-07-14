import json
import os
import requests
import re
from dotenv import load_dotenv
from langchain_core.documents import Document

load_dotenv(override=True)

def get_list_no_trx_so_from_query(query):
    pattern = r'SO(?:-BR\d{4})?-\d{4}-\d{8}|DRAFT\d{6}'
    matches = re.findall(pattern, query)
    return matches
    
def req_data():
    params = {
        "scopes": "filterRespo",
        "detail": "true",
        "join": "true",
        "paginate": 250
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('T_SO_BEARER_TOKEN')}",
        "Accept": "application/json",
    }
    response = requests.get(
        os.getenv("T_SO_API_ENDPOINT"),
        headers=headers,
        params=params,
        timeout=30
    )
    response.raise_for_status()
    return response.json().get("data", [])

def req_data_testing():
    with open("data_sales_order_periode_8_juni_2026.json", "r", encoding="utf-8") as f:
        so_data_as_json = json.load(f)

    return so_data_as_json

def get_as_a_list_document() -> list[Document]:
    params = {
        "scopes": "filterRespo",
        "detail": "true",
        "join": "true",
        "paginate": 250
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('T_SO_BEARER_TOKEN')}",
        "Accept": "application/json",
    }
    response = requests.get(
        os.getenv("T_SO_API_ENDPOINT"),
        headers=headers,
        params=params,
        timeout=30
    )
    response.raise_for_status()
    data = response.json().get("data", [])
    return [
        Document(
            page_content=(
                f"Business Unit: {so.get('comp.name')}, "
                f"Sub Business Unit: {so.get('sub_comp.name')}, "
                f"Cabang: {so.get('branch.name')}, "
                f"No. TRX SO: {so.get('no')}, "
                f"SO Date: {so.get('date')}, "
                f"SO Type: {so.get('type')}, "
                f"Item Type: {so.get('item_type.value1')}, "
                f"Customer Type: {so.get('cust_type.value1')}, "
                f"Pemasaran: {so.get('pemasaran.value1')}, "
                f"Pembayaran: {so.get('pembayaran.value1')}, "
                f"Customer: {so.get('cust_name')}, "
                f"Alamat Customer: {so.get('cust_addr')}, "
                f"No. NPWP: {so.get('cust_npwp')}, "
                f"Nama NPWP: {so.get('cust_npwpname')}, "
                f"Contact Person: {so.get('cust_cp')}, "
                f"No. PO Customer: {so.get('cust_no_po')}, "
                f"Bill To: {so.get('ship.name')}, "
                f"Bill To Address: {so.get('ship.addr')}, "
                f"Order Type 1: {so.get('order_type1.value1')}, "
                f"Order Type 2: {so.get('order_type2.value1')}, "
                f"PPN Type: {so.get('ppn_type')}, "
                f"SO Prospek: {so.get('is_prospek')}, "
                f"Nama Penerima: {so.get('ship.name')}, "
                f"Alamat: {so.get('ship.addr')}, "
                f"Due Date: {so.get('ship_duedate')}, "
                f"Payment Term: {so.get('pay_term.value1')}, "
                f"Project: {so.get('project')}, "
                f"Down Payment Percentage: {so.get('dp_pct')}, "
                f"Down Payment Amount: {so.get('dp_amt')}, "
                f"Currency: {so.get('currency.name')}, "
                f"Exchange Rate: {so.get('currency_rate')}, "
                f"Catatan: {so.get('note')}, "
                f"Status: {so.get('status.value1')}, "
                f"Est. Ekspedisi Percentage: {so.get('exp_pct')}, "
                f"Est. Ekspedisi Amount: {so.get('exp_amt')}, "
                f"Est. Operasional Percentage: {so.get('ops_pct')}, "
                f"Est. Operasional Amount: {so.get('ops_amt')}, "
                f"Total Amount: {so.get('amt')}, "
                f"Total Discount Amount: {so.get('disc_amt')}, "
                f"DPP: {so.get('dpp')}, "
                f"PPN Percent: {so.get('ppn_pct')}, "
                f"PPN Amount: {so.get('ppn_amt')}, "
                f"Grand Total: {so.get('netto')}"   
            )
        )
        for so in data
    ]

def get_as_a_list_document_for_testing():
    with open("data_sales_order_periode_8_juni_2026.json", "r", encoding="utf-8") as f:
        so_data_as_json = json.load(f)
    return [
        Document(
            page_content=", ".join(
                f"{key}: {value}"
                for key, value in so.items()
            ),
            metadata={"No. TRX SO": so.get("No. TRX SO")},
        )
        for so in so_data_as_json
    ]

def download_as_a_json():
    params = {
        "scopes": "filterRespo",
        "detail": "true",
        "join": "true",
        "paginate": 250
    }
    headers = {
        "Authorization": f"Bearer {os.getenv('T_SO_BEARER_TOKEN')}",
        "Accept": "application/json",
    }
    response = requests.get(
        os.getenv("T_SO_API_ENDPOINT"),
        headers=headers,
        params=params,
        timeout=30
    )
    response.raise_for_status()
    data_buffer = response.json().get("data", [])
    data = [
        {
            "Business Unit": so.get("comp.name"),
            "Sub Business Unit": so.get("sub_comp.name"),
            "Cabang": so.get("branch.name"),
            "No. TRX SO": so.get("no"),
            "SO Date": so.get("date"),
            "SO Type": so.get("type"),
            "Item Type": so.get("item_type.value1"),
            "Customer Type": so.get("cust_type.value1"),
            "Pemasaran": so.get("pemasaran.value1"),
            "Pembayaran": so.get("pembayaran.value1"),
            "Customer": so.get("cust_name"),
            "Alamat Customer": so.get("cust_addr"),
            "No. NPWP": so.get("cust_npwp"),
            "Nama NPWP": so.get("cust_npwpname"),
            "Contact Person": so.get("cust_cp"),
            "No. PO Customer": so.get("cust_no_po"),
            "Bill To": so.get("ship.name"),
            "Bill To Address": so.get("ship.addr"),
            "Order Type 1": so.get("order_type1.value1"),
            "Order Type 2": so.get("order_type2.value1"),
            "PPN Type": so.get("ppn_type"),
            "SO Prospek": so.get("is_prospek"),
            "Nama Penerima": so.get("ship.name"),
            "Alamat": so.get("ship.addr"),
            "Due Date": so.get("ship_duedate"),
            "Payment Term": so.get("pay_term.value1"),
            "Project": so.get("project"),
            "Down Payment Percentage": so.get("dp_pct"),
            "Down Payment Amount": so.get("dp_amt"),
            "Currency": so.get("currency.name"),
            "Exchange Rate": so.get("currency_rate"),
            "Catatan": so.get("note"),
            "Status": so.get("status.value1"),
            "Est. Ekspedisi Percentage": so.get("exp_pct"),
            "Est. Ekspedisi Amount": so.get("exp_amt"),
            "Est. Operasional Percentage": so.get("ops_pct"),
            "Est. Operasional Amount": so.get("ops_amt"),
            "Total Amount": so.get("amt"),
            "Total Discount Amount": so.get("disc_amt"),
            "DPP": so.get("dpp"),
            "PPN Percent": so.get("ppn_pct"),
            "PPN Amount": so.get("ppn_amt"),
            "Grand Total": so.get("netto"),
        }
        for so in data_buffer
    ]

    with open("data_sales_order_periode_8_juni_2026.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print("data_sales_order_periode_8_juni_2026.json berhasil diunduh dan disimpan.")