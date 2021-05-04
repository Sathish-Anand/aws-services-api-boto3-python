#!/bin/bash
    echo "----------------------------------"
    echo " Version Checks and Installations "
    echo "----------------------------------"

#Python Version Check
if command -v 'python3.7'
then
  echo "Python installed."
else
  echo "Python is NOT installed!"
  sudo add-apt-repository ppa:deadsnakes/ppa -y
  sudo apt-get update
  sudo apt-get install python3.7 -y
  sudo apt install python3-pip -y
  sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 2
fi

#Pip3 Version Check
if command -v pip3 &> /dev/null
then
  echo "Pip3 installed."
else
  echo "Pip3 is NOT installed!"
  sudo apt update
  sudo apt install python3-pip -y
fi

#Boto3 Version Check
if pip3 show boto3 | grep "Name:\sboto3";
then
  echo "Boto3 installed."
else
  echo "Boto3 is NOT installed so Installing Boto3!"
  python3 -m pip install boto3 botocore
fi

#pandas Version Check
if pip3 show pandas | grep "Name:\spandas";
then
  echo "Pandas installed."
else
  echo "Pandas is NOT installed so Installing Pandas!"
  python3 -m pip install pandas
fi

#AWS CLI Version Check
if command -v aws &> /dev/null
then
  echo "AWS CLI installed."
else
  echo "AWS CLI is NOT installed!"
fi
