import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# --- Streamlit UI Config ---
st.set_page_config(page_title="Global Product Price Comparator", layout="wide")
st.title("🛒 E-commerce Price Comparator")
st.write("Compare prices from Amazon, Flipkart, Ebay, Best Buy, and Newegg.")

# --- Input Fields ---
product_name = st.text_input("Enter product name to search:", "Macbook M2")
search_clicked = st.button("Search & Compare")

# --- Initialize Global Variables ---
aprice = None
price = None
number = None
bnumber = None
first_product_price = None

# --- Scraper Functions (Unchanged Logic) ---
def amazonscrap(product):
    global aprice
    driver = webdriver.Chrome()
    try:
        driver.get("https://www.amazon.in")
        time.sleep(5)
        search = driver.find_element(By.ID, "twotabsearchtextbox")
        search.send_keys(product)
        search.send_keys(Keys.ENTER)
        time.sleep(3)
        try:
            aprice_str = driver.find_element(By.XPATH, "(//span[@class='a-price-whole'])[1]").text
            aprice = int(aprice_str.replace(",", ""))
            print("Amazon Price: ", aprice)
        except:
            print("Amazon Product not found")
            aprice = 2000
    finally:
        driver.quit()

def flipkartscrap(product):
    global price
    driver = webdriver.Chrome()
    try:
        driver.get("https://www.flipkart.com")
        time.sleep(5)
        try:
            closebtn = driver.find_element(By.XPATH, "//button[contains(text(),'✕')]")
            closebtn.click()
        except:
            pass
        search = driver.find_element(By.NAME, "q")
        search.send_keys(product)
        search.send_keys(Keys.RETURN)
        time.sleep(3)
        try:
            price_str = driver.find_element(By.XPATH, "(//div[@data-id]//div[contains(text(), '₹')])[1]").text
            price = int(price_str.replace("₹", "").replace(",", "").strip()) / 94.25
            print("Flipkart Price: ", price)
        except:
            print("Flipkart Product not found")
    finally:
        driver.quit()

def ebayscrap(product):
    global number
    driver = webdriver.Chrome()
    try:
        driver.get("https://www.ebay.com/")
        driver.maximize_window()
        search = driver.find_element(By.ID, "gh-ac")
        search.send_keys(product)
        search.send_keys(Keys.ENTER)
        time.sleep(5)
        prices = driver.find_elements(By.XPATH, '//span[contains(@class,"s-card__price")]')
        for p in prices:
            text = p.get_attribute("innerText").strip()
            if text == "":
                continue
            if "to" in text.lower():
                continue
            try:
                number = float(text.replace("$", "").replace(",", "").split()[0])
                if number > 100:
                    print("Ebay Price:", number)
                    break
            except:
                continue
    finally:
        driver.quit()

def bestbuyscrap(product):
    global bnumber
    driver = webdriver.Chrome()
    try:
        driver.get("https://www.bestbuy.com/")
        driver.maximize_window()
        search = driver.find_element(By.ID, "autocomplete-search-bar")
        search.send_keys(product)
        search.send_keys(Keys.ENTER)
        time.sleep(5)
        prices = driver.find_elements(By.XPATH, '//span[contains(@class,"leading-6")]')
        for p in prices:
            btext = p.get_attribute("innerText").strip()
            if btext == "":
                continue
            if "to" in btext.lower():
                continue
            try:
                bnumber = float(btext.replace("$", "").replace(",", "").split()[0])
                if bnumber > 100:
                    print("Best Buy Price:", bnumber)
                    break
            except:
                continue
    finally:
        driver.quit()

def neweggscrap(product):
    global first_product_price
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    try:
        driver.get("https://www.newegg.com/")
        search = driver.find_element(By.XPATH, "//input[contains(@title,'Search Site')]")
        search.send_keys(product)
        search.send_keys(Keys.ENTER)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'item-cell')]"))
        )
        price_element = driver.find_element(By.XPATH, "(//div[contains(@class,'item-cell')])[1]//li[contains(@class,'price-current')]")
        price_text = price_element.text
        first_product_price = float(price_text.replace("$", "").replace(",", "").strip())
        print("Newegg Price:", first_product_price)
    except:
        print("Newegg Product not found")
    finally:
        driver.quit()

# --- Execution ---
if search_clicked:
    with st.spinner(f"Scraping prices for '{product_name}' across platforms... This may take a minute!"):
        # Running the scrapers
        amazonscrap(product_name)
        flipkartscrap(product_name)
        ebayscrap(product_name)
        bestbuyscrap(product_name)
        neweggscrap(product_name)

    # Dictionary to collect results
    dict1 = {
        "Amazon": aprice,
        "Flipkart": price,
        "Ebay": number,
        "Best Buy": bnumber,
        "New Egg": first_product_price,
    }

    # Filter out None values to prevent min() errors
    valid_prices = {k: v for k, v in dict1.items() if v is not None}

    st.subheader("Comparison Results")
    
    if valid_prices:
        # Find the minimum
        minimum = min(valid_prices.values())
        cheapest_store = ""
        for store, val in valid_prices.items():
            if val == minimum:
                cheapest_store = store
                break

        # Display Metrics in UI
        st.success(f"🎉 The minimum price is from **{cheapest_store}** and the price is **${minimum:.2f}**")
        
        st.markdown("### All Found Prices:")
        for store, price in valid_prices.items():
            st.metric(label=store, value=f"${price:.2f}")
    else:
        st.error("Could not find any prices or the scrapers failed to locate the product.")