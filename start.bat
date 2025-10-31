#!/bin/bash
git add .
git commit -m "Auto update $(date)"
git push
echo "✅ Code đã được đẩy lên GitHub thành công!"