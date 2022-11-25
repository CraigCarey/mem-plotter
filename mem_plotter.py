#!/usr/bin/env python3

import streamlit as st
import pandas as pd
import numpy as np
import psutil
import os
import time

st.title('Memory Consumption Plotter')

window_size = 10
refresh_secs = 5

def get_cpu_memory_consumption(pid: int):
    process = psutil.Process(pid).as_dict(attrs=['memory_info'])
    rss_kb = process['memory_info'].rss // 1024
    return rss_kb

def get_gpu_memory_consumption(pid: int):
    stream = os.popen(f"nvidia-smi | grep {pid}")
    output = stream.read()
    gpu_mb = np.float64(output.split()[7].replace("MiB", "", 1))
    return gpu_mb

def get_data(pid: int, gpu_used: bool = False):
    cpu_kb = get_cpu_memory_consumption(pid)
    cpu_mb = cpu_kb // 1024

    if (gpu_used):
        gpu_mb = get_gpu_memory_consumption(pid)
        new_row = {'cpu_kb': cpu_kb, 'cpu_mb': cpu_mb, 'gpu_mb': gpu_mb}
    else:
        new_row = {'cpu_kb': cpu_kb, 'cpu_mb': cpu_mb}

    return new_row

def using_gpu(pid: int) -> bool:
    stream = os.popen(f"nvidia-smi | grep {pid}")
    output = stream.read()
    return bool(output)

def plot_mem(pid: int):
    gpu_used = using_gpu(pid)
    if gpu_used:
        df = pd.DataFrame({'cpu_kb': [], 'cpu_mb': [], 'gpu_mb': []})
    else:
        df = pd.DataFrame({'cpu_kb': [], 'cpu_mb': []})
        
    st.subheader('CPU Memory Consumption (MB)')
    cpu_mb_chart_placeholder = st.empty()

    st.subheader('CPU Memory Consumption (KB)')
    cpu_kb_chart_placeholder = st.empty()    

    if gpu_used:
        st.subheader('GPU Memory Consumption (MB)')
        gpu_chart_placeholder = st.empty()

    df_describe_placeholder = st.empty()

    cnt = 0

    while True:

        new_row = get_data(pid, gpu_used)
        
        df = pd.concat([df, pd.DataFrame.from_records([new_row])], ignore_index=True)

        df['cpu_mb_ma'] = df.rolling(window=window_size)['cpu_mb'].mean()
        df['cpu_kb_ma'] = df.rolling(window=window_size)['cpu_kb'].mean()

        if (gpu_used):
            df['gpu_mb_ma'] = df.rolling(window=window_size)['gpu_mb'].mean()

        if (cnt % refresh_secs == 0):
            cpu_mb_chart_placeholder.line_chart(data=df[['cpu_mb', 'cpu_mb_ma']])
            cpu_kb_chart_placeholder.line_chart(data=df[['cpu_kb', 'cpu_kb_ma']])

            if (gpu_used):
                gpu_chart_placeholder.line_chart(data=df[['gpu_mb', 'gpu_mb_ma']])

            df_describe_placeholder.write(df.describe(include='all'))

            df.to_pickle(f"{pid}.dat")

        cnt = cnt + 1
        
        time.sleep(1)

form = st.form("template_form")
pid = form.text_input('PID')
refresh_secs = int(form.text_input(label='Refresh (s)', value=f"{refresh_secs}"))
window_size = int(form.text_input(label='Rolling avg win', value=f"{window_size}"))
submit = form.form_submit_button("Start")

if submit:
    plot_mem(int(pid))
