import streamlit as st
import sys

st.set_page_config(page_title="App Diagnostics", page_icon="🔧")

st.title("🔧 App Diagnostics")

st.subheader("Python Information")
st.write(f"Python version: {sys.version}")

st.subheader("Installed Packages")
try:
    import pkg_resources
    packages = [f"{pkg.key}=={pkg.version}" for pkg in pkg_resources.working_set]
    st.write(packages[:20])  # Show first 20 packages
except:
    st.write("Could not list packages")

st.subheader("Test Components")

if st.button("Test Basic Streamlit"):
    st.success("Streamlit is working!")
    st.write("This is a test message")
    st.dataframe({"test": [1, 2, 3], "data": [4, 5, 6]})

if st.button("Test Imports"):
    try:
        import pandas as pd
        st.success("✅ pandas imported")
    except Exception as e:
        st.error(f"❌ pandas: {e}")
    
    try:
        import ccxt
        st.success("✅ ccxt imported")
    except Exception as e:
        st.error(f"❌ ccxt: {e}")
    
    try:
        import plotly
        st.success("✅ plotly imported")
    except Exception as e:
        st.error(f"❌ plotly: {e}")
    
    try:
        import ta
        st.success("✅ ta imported")
    except Exception as e:
        st.error(f"❌ ta: {e}")

st.subheader("Troubleshooting")
st.markdown("""
If you see a blank screen:

1. **Check the terminal** for error messages
2. **Run this diagnostic** to test components
3. **Ensure all packages are installed**: `pip install -r requirements.txt`
4. **Try a different browser**
5. **Clear browser cache** and restart Streamlit

**Common fixes:**
- Reinstall packages: `pip install --force-reinstall -r requirements.txt`
- Update Streamlit: `pip install --upgrade streamlit`
- Run on different port: `streamlit run main.py --server.port 8502`
""")