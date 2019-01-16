# Note: Since git repositories are cloned, an active internet connection is required

# The predictions were performed on Debian 9 (stretch)
FROM debian:stretch

# Set the working directory to /app
WORKDIR /application

# Set up specific apt package repositories (if needed)
RUN apt update

# Install git
RUN apt install -y -qq git

# Clone the supplementary website containing the data for the measurements and predictions
RUN git clone https://github.com/ChristianKaltenecker/Distance-Based_Data

# Setup SPL Conqueror

# Install Mono and nuget for executing SPL Conqueror
RUN apt install -y -qq mono-complete nuget

# Download SPL Conqueror and set it to the same commit as in the paper -- this may take some time
RUN git clone https://github.com/se-passau/SPLConqueror && cd SPLConqueror && git reset --hard 8d5e442f0e085f8df6d7807ca69c65deeae7e0b3

# TODO
RUN wget https://github.com/Z3Prover/z3/releases/download/z3-4.7.1/z3-4.7.1-x64-debian-8.10.zip && 

# Next, restore NuGet packages and build the whole project
RUN cd SPLConqueror/SPLConqueror/ && nuget restore ./ && xbuild /p:Configuration=Release SPLConqueror.sln

# Setup for the additional scripts

# Install Python and R for executing the scripts
RUN apt install -y -qq python3 r-recommended

# TODO: Install the dependend python packages and R packages

# Clone the scripts
RUN git clone https://github.com/ChristianKaltenecker/Distance-Based_Sampling
