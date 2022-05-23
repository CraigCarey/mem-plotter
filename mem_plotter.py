#!/usr/bin/env python3

import streamlit as st
import pandas as pd
import numpy as np
import psutil
import os
import time

st.title('Memory Consumption Plotter')

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

    if (gpu_used):
        gpu_kb = get_gpu_memory_consumption(pid)
        new_row = {'cpu': cpu_kb, 'gpu': gpu_kb}
    else:
        new_row = {'cpu': cpu_kb}

    return new_row

def using_gpu(pid: int) -> bool:
    stream = os.popen(f"nvidia-smi | grep {pid}")
    output = stream.read()
    return bool(output)

def plot_mem(pid: int):
    gpu_used = using_gpu(pid)
    if gpu_used:
        df = pd.DataFrame({'cpu': [], 'gpu': []})    
    else:
        df = pd.DataFrame({'cpu': []})
        

    st.subheader('CPU Memory Consumption (KB)')
    cpu_placeholder = st.empty()

    if gpu_used:
        st.subheader('GPU Memory Consumption (MB)')
        gpu_placeholder = st.empty()

    while True:
        new_row = get_data(pid, gpu_used)
        
        df = pd.concat([df, pd.DataFrame.from_records([new_row])], ignore_index=True)

        cpu_placeholder.line_chart(data=df['cpu'])

        if (gpu_used):
            gpu_placeholder.line_chart(data=df['gpu'])

        time.sleep(1)

form = st.form("template_form")
pid = form.text_input('PID') # 14294
submit = form.form_submit_button("Start")

if submit:
    plot_mem(int(pid))
