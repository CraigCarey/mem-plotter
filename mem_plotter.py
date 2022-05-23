#!/usr/bin/env python3

import streamlit as st
import pandas as pd
import numpy as np
import psutil

# st.title('Memory Consumption Plotter')

def get_cpu_memory_consumption(pid: int):
    process = psutil.Process(pid).as_dict(attrs=['memory_info'])
    rss_kb = process['memory_info'].rss // 1024
    return rss_kb

def get_gpu_memory_consumption(pid: int):
    pass
    
rss_kb = get_cpu_memory_consumption(328460)

print(rss_kb)
