---

source_id: grocerspy
source_type: project
title: GrocerSpy — Grocery Price Comparison Tool
url: https://github.com/Premx24/GrocerSpy
-----------------------------------------

# Overview

GrocerSpy is a Python-based intelligent grocery price comparison tool that helps users compare grocery prices across Blinkit, Swiggy Instamart, and JioMart.

Users can enter multiple grocery products during a session. GrocerSpy uses browser automation to retrieve product listings and fuzzy string matching to identify the most relevant products. It then presents the results in a tabular format and identifies the platform offering the lowest price for each product.

# Problem

Comparing grocery prices across multiple online platforms manually can be time-consuming. Users may need to search for the same product on several platforms and compare the resulting prices individually.

GrocerSpy was built to automate this process and provide the comparison through a single command-line workflow.

# Solution

* Users enter multiple grocery product names.
* Playwright automates browser-based product searches.
* Product listings are retrieved from Blinkit, Swiggy Instamart, and JioMart.
* Fuzzy string matching is used to identify the most relevant product listings.
* Prices are extracted from the matched products.
* Results are presented in a tabular format.
* The platform with the lowest price is identified for each product.

# Tech Stack

## Language

* Python

## Libraries and Tools

* Playwright
* pandas
* thefuzz
* rich

## Browser Automation

* Playwright
* Headless browser automation

# Key Features

## Interactive Input

Users can enter multiple grocery products during a single session.

## Automated Price Retrieval

Playwright is used to automate browser interactions and retrieve product listings from grocery platforms.

## Cross-Platform Price Comparison

GrocerSpy compares prices across:

* Blinkit
* Swiggy Instamart
* JioMart

## Fuzzy String Matching

The `thefuzz` library is used to find the best matching product when product names or listings differ between platforms.

## Tabular Results

The application presents the retrieved prices in a comparison table.

## Lowest Price Detection

For each product, GrocerSpy identifies the platform offering the lowest retrieved price.

# How It Works

1. The user enters one or more grocery product names.
2. GrocerSpy launches automated browser workflows using Playwright.
3. The application searches for the products across Blinkit, Swiggy Instamart, and JioMart.
4. Product listings are retrieved from each platform.
5. Fuzzy string matching identifies the most relevant listing.
6. The corresponding prices are extracted.
7. The results are displayed in a comparison table.
8. The platform with the lowest price is highlighted for each product.

# Example

For a product such as Amul Milk 1L, GrocerSpy can compare retrieved prices across different platforms.

Example:

| Product      | Blinkit | Swiggy Instamart | JioMart | Best Site |
| ------------ | ------: | ---------------: | ------: | --------- |
| Amul Milk 1L |  ₹55.00 |           ₹56.00 |  ₹58.00 | Blinkit   |
| Rice 200 Gm  |  ₹32.00 |           ₹28.50 |  ₹27.00 | JioMart   |

The best price is automatically identified from the retrieved results.

# Installation

```text
git clone <repository-url>
cd GrocerSpy

python -m venv venv
source venv/bin/activate

pip install playwright pandas thefuzz rich
playwright install

python grocerspy.py
```

# Compatibility

GrocerSpy is designed to work on:

* Windows
* macOS
* Linux

# Project Information

* Project: GrocerSpy
* Dates: August 2025 – October 2025
* Type: Grocery price comparison tool
* Language: Python
* Video demo: https://youtu.be/3QCe6qFqswI

# Project Goal

GrocerSpy was created to simplify grocery price comparison by automating the process of searching multiple online grocery platforms and identifying the lowest retrieved price for each product.

The goal is to help users reduce the time required to compare prices and make more informed purchasing decisions.

# Important Limitations

* Prices depend on the product listings retrieved at the time of the search.
* Product matching depends on fuzzy string matching.
* The project retrieves information from the supported grocery platforms through browser automation.
* The documentation does not provide guaranteed pricing accuracy or availability.
* The project should not claim to provide historical or guaranteed prices unless supported by another source.

# Resume Facts

* Built an intelligent grocery price comparison tool to aggregate product prices across Blinkit, Swiggy Instamart, and JioMart.
* Developed automated browser workflows using Playwright to retrieve real-time product listings.
* Implemented fuzzy string matching using the `thefuzz` library to identify relevant products across websites.
* Generated tabular price comparisons highlighting the lowest-priced platform for each product.
* Technologies: Python, Playwright, pandas, thefuzz.

# Grounding Rules

* Do not invent grocery prices or claim that a particular platform currently has the lowest price unless the source provides that data.
* Do not claim GrocerSpy supports grocery platforms other than Blinkit, Swiggy Instamart, and JioMart unless another source confirms it.
* Do not claim a product was successfully found if the available source does not confirm it.
* When discussing fuzzy matching, identify `thefuzz` as the library used.
* When discussing browser automation, identify Playwright as the tool used.
* If a requested implementation detail is not documented here, state that the available GrocerSpy documentation does not provide that information.
* Do mention about the demo video and mention that video in the ui, if required