# 🔍 Spot the Difference Game

## 📋 Assignment Information
- **Course:** HITI 37 - Image Processing & GUI Development
- **Assignment:** Group Assignment 3 (30% of total grade)
- **Date:** May 2026

## 👥 Group Members

| # | Name | GitHub Username | Role |
|---|------|----------------|------|
| 1 | Group Members:
- [Ozair khalid      ID: 401294] - [Ozair20020563]
- [Md Naimur Islam   ID: S397051] - [Durjoy09]
- [Group Member 3 Full Name] - [GitHub Username]

## 🎮 Game Description

A desktop "Spot the Difference" game where players find hidden differences between two nearly identical images. The game demonstrates Object-Oriented Programming principles, GUI development using Tkinter, and image processing using OpenCV.

## ✨ Features

### Core Features
- ✅ Load any image (JPG, PNG, BMP formats)
- ✅ Automatically generates **5 random differences** in the modified image
- ✅ **3 types of alterations**: Blur, Pixelate, and Contrast Change
- ✅ Differences are randomly positioned and non-overlapping
- ✅ Side-by-side image display with aspect ratio preservation

### Gameplay Features
- ✅ **Click detection** on modified image with coordinate conversion
- ✅ **Score tracking**: Found differences counter (0/5)
- ✅ **Mistake system**: Maximum 3 mistakes per image
- ✅ **Visual feedback**: Red circles for correct guesses
- ✅ **Reveal button**: Shows all unfound differences in blue
- ✅ **Game over popup**: Appears after 3 mistakes or finding all differences
- ✅ **Reset functionality**: Loading new image resets all counters

### Technical Features
- ✅ Object-Oriented Programming (3+ classes)
- ✅ Inheritance with abstract base class
- ✅ Polymorphism for image alterations
- ✅ Encapsulation with private attributes
- ✅ Exception handling for image loading errors

## 🛠️ Technologies Used

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.8+ | Core programming language |
| Tkinter | Built-in | GUI framework |
| OpenCV | 4.8.1 | Image processing and manipulation |
| Pillow | 10.1.0 | Image handling and display |
| NumPy | 1.24.3 | Array operations for images |

## 📦 Installation

### Prerequisites
- Python 3.8 or higher installed on your system
- pip package manager

### Step 1: Clone the Repository
```bash
git clone https://github.com/Ozair20020563/Assignment-3.git
cd Assignment-3