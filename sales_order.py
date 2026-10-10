import json
import os
import requests
import re
from dotenv import load_dotenv
from langchain_core.documents import Document

load_dotenv(override=True)
    
def get_as_a_json():
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
    return [
            {
            "business_unit": so.get("comp.name"),
            "sub_business_unit": so.get("sub_comp.name"),
            "cabang": so.get("branch.name"),
            "trx_so": so.get("no"),
            "so_date": so.get("date"),
            "so_type": so.get("type"),
            "item_type": so.get("item_type.value1"),
            "customer_type": so.get("cust_type.value1"),
            "pemasaran": so.get("pemasaran.value1"),
            "pembayaran": so.get("pembayaran.value1"),
            "customer": so.get("cust_name"),
            "alamat_customer": so.get("cust_addr"),
            "npwp": so.get("cust_npwp"),
            "nama_npwp": so.get("cust_npwpname"),
            "contact_person": so.get("cust_cp"),
            "customer_po": so.get("cust_no_po"),
            "bill_to": so.get("ship.name"),
            "bill_to_address": so.get("ship.addr"),
            "order_type_1": so.get("order_type1.value1"),
            "order_type_2": so.get("order_type2.value1"),
            "ppn_type": so.get("ppn_type"),
            "so_prospek": so.get("is_prospek"),
            "nama_penerima": so.get("ship.name"),
            "alamat": so.get("ship.addr"),
            "due_date": so.get("ship_duedate"),
            "payment_term": so.get("pay_term.value1"),
            "project": so.get("project"),
            "down_payment_percentage": so.get("dp_pct"),
            "down_payment_amount": so.get("dp_amt"),
            "currency": so.get("currency.name"),
            "exchange_rate": so.get("currency_rate"),
            "catatan": so.get("note"),
            "status": so.get("status.value1"),
            "est_ekspedisi_percentage": so.get("exp_pct"),
            "est_ekspedisi_amount": so.get("exp_amt"),
            "est_operasional_percentage": so.get("ops_pct"),
            "est_operasional_amount": so.get("ops_amt"),
            "total_amount": so.get("amt"),
            "total_discount_amount": so.get("disc_amt"),
            "dpp": so.get("dpp"),
            "ppn_percent": so.get("ppn_pct"),
            "ppn_amount": so.get("ppn_amt"),
            "grand_total": so.get("netto")
        }
        for so in response.json().get("data", [])
    ]

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