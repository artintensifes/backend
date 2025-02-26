#!/bin/bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:10000 main:app --timeout 120
