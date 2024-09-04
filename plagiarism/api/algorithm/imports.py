
import logging
import re

import spacy
import urllib3
from langdetect import detect
from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from tika import language

# Set the logging level to ERROR to suppress informational messages
logging.getLogger("stanza").setLevel(logging.ERROR)

urllib3.disable_warnings()
# preprocess_text_uk
import json

# main
import os
import pickle
import pprint
import random
import re
import time
from collections import Counter
from dataclasses import dataclass
from multiprocessing import Pool, freeze_support
from typing import Dict, Union

import joblib
import nltk
import requests
import spacy
import tika
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.util import ngrams
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tika import language, parser

tika.initVM()

from api.algorithm.API_keys import API_KEY, CSE_ID, CUSTOM_TOKEN_KEY, KEY_OPENAI
from api.algorithm.constants import *
from tika import language, parser
from urllib3.exceptions import InsecureRequestWarning

logging.getLogger("stanza").setLevel(logging.ERROR)


nlp = spacy.load("en_core_web_sm")
nlp.max_length = 15000000000

import torch
from transformers import BertModel, BertTokenizer
