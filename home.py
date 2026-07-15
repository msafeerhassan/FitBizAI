from flask import Blueprint, jsonify
from ai import runAIdaily
from db import saveData, loadUserProfile, loadFullRecordData
from layout import renderPage
from datetime import date,timedelta

homeBp = Blueprint("home", __name__)

def todaySummary(history):
    todayStr = date.today().isoformat()

    summary = {
        "diet": [],
        "water": 0.0,
        "workout": [],
        "context": [],
        "productivity": 0.0
    }

    if not history:
        return summary
    for item in history.get("diet", []):
        if item.get("date") == todayStr:
            summary["diet"].append(item)
    
    for item in history.get("water", []):
        if item.get("date") == todayStr:
            summary["water"] += float(item.get("amount", 0))
    
    for item in history.get("workout", []):
        if item.get("date") == todayStr:
            summary["workout"].append(item)
    for item in history.get("context", []):
        if item.get("date") == todayStr:
            summary["context"].append(item)
    for item in history.get("productivity", []):
        if item.get("date") == todayStr:
            summary["productivity"] += float(item.get("time_spent", 0))
    
    return summary

def calculateStreak(history):
    if not history:
        return 0
    
    reviewDates = set()
    for review in history.get("ai_reviews", []):
        try:
            reviewDates.add(date.fromisoformat(review.get("date")))
        except (ValueError, TypeError):
            continue
    
    if not reviewDates:
        return 0
    
    checkDate = date.today()

    if checkDate not in reviewDates:
        checkDate -= timedelta(days=1)
        if checkDate not in reviewDates:
            return 0

    streak = 0

    while checkDate in reviewDates:
        streak += 1
        checkDate -= timedelta(days=1)
    
    return streak

def getDayTotal(history, category, checkDate, valueKey=None, mode="sum"):
    if not history:
        return 0.0
    
    checkDateStr = checkDate.isoformat()
    records = history.get(category, [])

    if mode == "count":
        count = 0
        for r in records:
            if r.get("date") == checkDateStr:
                count += 1
        
        return count
    total = 0.0

    for r in records:
        if r.get("date") == checkDateStr:
            total += float(r.get(valueKey, 0))
    
    return total

def calculateGoalStreak(history, category, targetVal, valueKey=None, mode="sum"):
    if not history:
        return 0
    
    checkDate = date.today()
    todayTotal = getDayTotal(history, category, checkDate, valueKey, mode)

    if todayTotal < targetVal:
        checkDate -= timedelta(days=1)

        if getDayTotal(history, category, checkDate, valueKey, mode) < targetVal:
            return 0
    
    streak = 0

    while getDayTotal(history, category, checkDate, valueKey, mode) >= targetVal:
        streak += 1
        checkDate -= timedelta(days=1)
    return streak

def todayReviewExist(history):
    todayStr = date.today().isoformat()

    if not history:
        return None
    
    for review in history.get("ai_reviews", []):
        if review.get("date") == todayStr:
            return review
    
    return None