# Note: Since git repositories are cloned, an active internet connection is required

# The predictions were performed on Debian 9 (stretch)
FROM debian:stretch

# Set the working directory to /app
WORKDIR /application

# Set up specific apt package repositories (if needed)
RUN apt update

# Install git and wget
RUN apt install -y -qq git wget unzip tar texlive

# Add dependency for z3
RUN apt install -y -qq libgomp1

# Clone the supplementary website containing the data for the measurements and predictions
RUN git clone --depth=1 https://github.com/ChristianKaltenecker/Distance-Based_Data.git \
    && tar -xzf Distance-Based_Data/SupplementaryWebsite/MeasuredPerformanceValues/JavaGC/measurements.tar.gz -C Distance-Based_Data/SupplementaryWebsite/MeasuredPerformanceValues/JavaGC/ \
    && tar -xzf Distance-Based_Data/SupplementaryWebsite/MeasuredPerformanceValues/VP9/measurements.tar.gz -C Distance-Based_Data/SupplementaryWebsite/MeasuredPerformanceValues/VP9/

# Setup SPL Conqueror

# Install Mono and nuget for executing SPL Conqueror
RUN apt install -y -qq mono-complete

# Download SPL Conqueror and set it to the same commit as in the paper -- this may take some time
RUN git clone https://github.com/se-passau/SPLConqueror.git \
    && cd SPLConqueror \
    && git reset --hard 4b4802d08e17e699886f360d94971a237bf73255 \
    && cd ..

# Download nuget
RUN cd SPLConqueror/SPLConqueror/ \
    && wget https://dist.nuget.org/win-x86-commandline/latest/nuget.exe \
    && cd ../../

# Download z3 (the library is needed for the constraint solver that is usedd inside SPL Conqueror)
RUN wget https://github.com/Z3Prover/z3/releases/download/z3-4.7.1/z3-4.7.1-x64-debian-8.10.zip \
    && unzip z3-4.7.1-x64-debian-8.10.zip \
    && rm z3-4.7.1-x64-debian-8.10.zip \
    && mv z3-4.7.1-x64-debian-8.10 z3 \
    && cp z3/bin/libz3.so /usr/lib/libz3.so

# Next, restore NuGet packages and build the whole project
RUN cd SPLConqueror \
    && git submodule update --init \
    && cd SPLConqueror/ \
    && mono nuget.exe restore ./ -MSBuildPath /usr/lib/mono/xbuild/14.0/bin \
    && xbuild /p:Configuration=Release /p:TargetFrameworkVersion="v4.5" /p:TargetFrameworkProfile="" ./SPLConqueror.sln \
    && cd ../..

# Setup for the additional scripts

# Install Python and R for executing the scripts
RUN apt install -y -qq python3 python3-numpy python3-scipy r-recommended

# Install the dependencies for Python and R
# As the packages for R will be compiled, this process may take a while
RUN apt install -y -qq python3-numpy python3-scipy libcurl4-openssl-dev \
    && Rscript /application/Distance-Based_Data/InstallPackages.R
