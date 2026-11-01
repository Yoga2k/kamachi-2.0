"""
ai/website_builder.py — Autonomous Website Generator & Vercel Deployer for KAMACHI 2.0.
Supports:
  - "write code web site for online shop and host in vercel"
  - Generating complete modern HTML/Tailwind/JS ecommerce websites with cart & checkout
  - Vercel deployment and local browser launch
"""

import os
import re
import sys
import shutil
import subprocess
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from utils import speak
except ImportError:
    def speak(text):
        print(f"[KAMACHI]: {text}")

SHOP_HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Yoga's Online Shop — Premium Store</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');
    body { font-family: 'Plus Jakarta Sans', sans-serif; }
  </style>
</head>
<body class="bg-slate-900 text-slate-100 min-h-screen">

  <!-- Navbar -->
  <header class="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-20 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center font-extrabold text-xl shadow-lg shadow-cyan-500/20">Y</div>
        <span class="text-2xl font-black tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">YOGA STORE</span>
      </div>
      
      <div class="flex items-center gap-4">
        <button onclick="toggleCart()" class="relative p-3 rounded-xl bg-slate-800 hover:bg-slate-700 transition flex items-center gap-2 border border-slate-700">
          <i class="fa-solid fa-cart-shopping text-cyan-400"></i>
          <span class="font-bold">Cart</span>
          <span id="cart-count" class="bg-cyan-500 text-slate-950 font-black text-xs px-2 py-0.5 rounded-full">0</span>
        </button>
      </div>
    </div>
  </header>

  <!-- Hero Section -->
  <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
    <span class="px-4 py-1.5 rounded-full text-xs font-bold tracking-wide uppercase bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 mb-4 inline-block">Built by Kamachi 2.0 AI</span>
    <h1 class="text-4xl sm:text-6xl font-black tracking-tight mb-6 mt-3">Next-Gen Tech & Lifestyle Shop</h1>
    <p class="text-slate-400 text-lg max-w-2xl mx-auto">Experience high-performance gear curated for developers, creators, and innovators. One-click shopping with instant checkout.</p>
  </section>

  <!-- Product Catalog -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-24">
    <div class="flex items-center justify-between mb-8">
      <h2 class="text-2xl font-bold">Featured Products</h2>
      <span class="text-sm text-slate-400">6 Products Available</span>
    </div>

    <div id="product-grid" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
      <!-- Injected via JavaScript -->
    </div>
  </main>

  <!-- Cart Drawer / Modal -->
  <div id="cart-drawer" class="fixed inset-y-0 right-0 max-w-md w-full bg-slate-800 border-l border-slate-700 shadow-2xl p-6 transform translate-x-full transition-transform duration-300 z-50 flex flex-col justify-between">
    <div>
      <div class="flex items-center justify-between pb-4 border-b border-slate-700">
        <h3 class="text-xl font-bold">Your Cart</h3>
        <button onclick="toggleCart()" class="text-slate-400 hover:text-white"><i class="fa-solid fa-xmark text-xl"></i></button>
      </div>
      <div id="cart-items" class="py-4 space-y-4 max-h-[60vh] overflow-y-auto">
        <p class="text-slate-500 text-center py-8">Your cart is empty.</p>
      </div>
    </div>

    <div class="border-t border-slate-700 pt-4">
      <div class="flex justify-between text-lg font-bold mb-4">
        <span>Total:</span>
        <span id="cart-total" class="text-cyan-400">₹0</span>
      </div>
      <button onclick="checkout()" class="w-full py-3.5 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-black rounded-xl shadow-lg transition">Checkout Now</button>
    </div>
  </div>

  <script>
    const products = [
      { id: 1, name: "Neural Wireless Headphones", price: 4999, img: "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500&q=80", tag: "Audio" },
      { id: 2, name: "Mechanical RGB Keyboard", price: 3499, img: "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=500&q=80", tag: "Tech" },
      { id: 3, name: "Minimalist Smart Watch Pro", price: 6299, img: "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=500&q=80", tag: "Wearables" },
      { id: 4, name: "Ultra-Fast NVMe SSD 1TB", price: 5499, img: "https://images.unsplash.com/photo-1597872200969-2b65d56bd16b?w=500&q=80", tag: "Hardware" },
      { id: 5, name: "Ergonomic Studio Mouse", price: 2199, img: "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500&q=80", tag: "Office" },
      { id: 6, name: "Studio Desk Ring Light", price: 1899, img: "https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=500&q=80", tag: "Lighting" }
    ];

    let cart = [];

    function renderProducts() {
      const grid = document.getElementById("product-grid");
      grid.innerHTML = products.map(p => `
        <div class="bg-slate-800/80 border border-slate-700/60 rounded-2xl p-4 flex flex-col justify-between hover:border-cyan-500/50 transition">
          <img src="${p.img}" alt="${p.name}" class="w-full h-48 object-cover rounded-xl mb-4">
          <div>
            <span class="text-xs text-cyan-400 font-semibold">${p.tag}</span>
            <h3 class="font-bold text-lg mt-1 mb-2">${p.name}</h3>
            <p class="text-xl font-black text-white">₹${p.price.toLocaleString()}</p>
          </div>
          <button onclick="addToCart(${p.id})" class="mt-4 w-full py-2.5 bg-slate-700 hover:bg-cyan-500 hover:text-slate-950 font-bold rounded-xl transition flex items-center justify-center gap-2">
            <i class="fa-solid fa-plus"></i> Add to Cart
          </button>
        </div>
      `).join("");
    }

    function toggleCart() {
      const drawer = document.getElementById("cart-drawer");
      drawer.classList.toggle("translate-x-full");
    }

    function addToCart(id) {
      const item = products.find(p => p.id === id);
      cart.push(item);
      updateCart();
    }

    function updateCart() {
      document.getElementById("cart-count").innerText = cart.length;
      const total = cart.reduce((sum, item) => sum + item.price, 0);
      document.getElementById("cart-total").innerText = "₹" + total.toLocaleString();

      const itemsContainer = document.getElementById("cart-items");
      if (cart.length === 0) {
        itemsContainer.innerHTML = '<p class="text-slate-500 text-center py-8">Your cart is empty.</p>';
      } else {
        itemsContainer.innerHTML = cart.map((item, idx) => `
          <div class="flex items-center justify-between bg-slate-900/60 p-3 rounded-xl border border-slate-700">
            <div>
              <p class="font-bold text-sm">${item.name}</p>
              <p class="text-xs text-cyan-400 font-semibold">₹${item.price.toLocaleString()}</p>
            </div>
            <button onclick="removeItem(${idx})" class="text-rose-400 hover:text-rose-300 text-sm"><i class="fa-solid fa-trash"></i></button>
          </div>
        `).join("");
      }
    }

    function removeItem(idx) {
      cart.splice(idx, 1);
      updateCart();
    }

    function checkout() {
      if (cart.length === 0) {
        alert("Cart is empty! Add products first.");
        return;
      }
      alert("🎉 Order placed successfully! Thank you for shopping with Yoga Store.");
      cart = [];
      updateCart();
      toggleCart();
    }

    renderProducts();
  </script>
</body>
</html>
"""

VERCEL_CONFIG = """{
  "version": 2,
  "name": "yoga-online-shop",
  "builds": [
    { "src": "index.html", "use": "@vercel/static" }
  ],
  "routes": [
    { "src": "/(.*)", "dest": "/index.html" }
  ]
}
"""


class WebsiteBuilder:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WebsiteBuilder, cls).__new__(cls)
        return cls._instance

    def build_and_deploy_shop(self, target_dir: Optional[str] = None) -> str:
        """
        Creates the complete online shop website and deploys to Vercel or opens browser.
        """
        base_dir = Path(target_dir or "d:/projects/online-shop")
        base_dir.mkdir(parents=True, exist_ok=True)

        # Write index.html
        html_file = base_dir / "index.html"
        with open(html_file, "w", encoding="utf-8") as f:
            f.write(SHOP_HTML_TEMPLATE)

        # Write vercel.json
        vercel_file = base_dir / "vercel.json"
        with open(vercel_file, "w", encoding="utf-8") as f:
            f.write(VERCEL_CONFIG)

        speak("Online shop website code generated successfully. Now initiating deployment...")

        # Record this in Kamachi work memory
        try:
            from memory.memory_store import get_memory_store
            get_memory_store().record_work(str(html_file), app_name="VS Code", project_name="Online Shop")
        except Exception:
            pass

        # Check if Vercel CLI is installed
        vercel_deployed = False
        vercel_url = ""
        try:
            res = subprocess.run(["vercel", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            if res.returncode == 0:
                speak("Deploying online shop to Vercel production...")
                deploy_res = subprocess.run(["vercel", "--yes", "--prod"], cwd=str(base_dir), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
                if deploy_res.returncode == 0:
                    vercel_deployed = True
                    # Look for URL in output
                    urls = re.findall(r"https://[a-zA-Z0-9\.\-_]+\.vercel\.app", deploy_res.stdout)
                    if urls:
                        vercel_url = urls[0]
        except Exception:
            pass

        # Open website locally in browser
        webbrowser.open(html_file.as_uri())

        if vercel_deployed and vercel_url:
            msg = f"Your online shop is live on Vercel at {vercel_url}! Also opened the live preview in your browser."
        else:
            msg = f"Your online shop website has been created in {base_dir} with full cart and checkout, and opened in your browser. Ready to deploy with Vercel CLI!"

        speak(msg)
        return msg

    def handle_command(self, command: str) -> str:
        cmd = command.lower().strip()
        if any(k in cmd for k in ["online shop", "e-commerce", "ecommerce", "shopping website"]):
            return self.build_and_deploy_shop()
        return self.build_and_deploy_shop()


def get_website_builder() -> WebsiteBuilder:
    return WebsiteBuilder()

