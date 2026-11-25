import streamlit as st
import os
import duckdb

def load_parquet_from_s3_or_local(s3_prefix, local_prefix, bucket_env="TAIFEX_S3_BUCKET", region_env="TAIFEX_S3_REGION"):
    con = duckdb.connect()
    con.execute("INSTALL httpfs; LOAD httpfs;")
    con.execute("INSTALL aws; LOAD aws;")

    try:
        S3_BUCKET = st.secrets.get(bucket_env, os.environ.get(bucket_env, ""))
        S3_REGION = st.secrets.get(region_env, os.environ.get(region_env, "ap-southeast-2"))
        if "AWS_ACCESS_KEY_ID" in st.secrets:
            con.execute(f"SET s3_access_key_id = '{st.secrets.AWS_ACCESS_KEY_ID}';")
            con.execute(f"SET s3_secret_access_key = '{st.secrets.AWS_SECRET_ACCESS_KEY}';")
    except Exception:
        S3_BUCKET = os.environ.get(bucket_env, "")
        S3_REGION = os.environ.get(region_env, "ap-southeast-2")
    con.execute(f"SET s3_region = '{S3_REGION}';")

    if S3_BUCKET:
        s3_path = f"s3://{S3_BUCKET}/{s3_prefix}/*.parquet"
        try:
            return con.execute(f"SELECT * FROM read_parquet('{s3_path}', hive_partitioning=true)").df()
        except Exception as e:
            st.error(f"S3 load failed: {e}")
            st.stop()

    local_path = f"{local_prefix}/*.parquet"
    return con.execute(f"SELECT * FROM read_parquet('{local_path}', hive_partitioning=true)").df()
