# 前提是你要安装 rpm-build
python setup.py bdist_rpm
echo "----------------------------------------------"
sleep 1
mv -f dist/pysvn-0.0.1-1.noarch.rpm ../install/
rm -rf build/ dist/ pysvn.egg-info/
echo 'ok'
