# PlayDMA

> NOTE: On Archlinux if you have aur and blackarch repositories openfpgaloader-bin, pcileech and memprocfs are in the repo.

## Setup the DMA card
Install [OpenFPGALoader](github.com/trabucayre/openFPGALoader) and download the CaptainDMA version for your PCI card from [PCILeech-FPGA](https://github.com/ufrisk/pcileech-fpga/tree/master/CaptainDMA), then upload the firmware to the SPI flash.
`openFPGALoader -c ch347_jtag -B -f ./pcileech_75t484_x1.bin`

## Install tools
Follow the guide at the [MemProcFS Wiki](https://github.com/ufrisk/MemProcFS/wiki/_Linux)

## Mount FS
`sudo memprocfs -device fpga -memmap auto -mount /mnt`

