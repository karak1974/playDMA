# PlayDMA

## Setup the DMA card
Install [OpenFPGALoader](https://github.com/trabucayre/openFPGALoader) and download the CaptainDMA version for your PCI card from [PCILeech-FPGA](https://github.com/ufrisk/pcileech-fpga/tree/master/CaptainDMA), then upload the firmware to the SPI flash.  
`openFPGALoader -c ch347_jtag -B -f ./pcileech_75t484_x1.bin`

## Install tools
Follow the guide at the [MemProcFS Wiki](https://github.com/ufrisk/MemProcFS/wiki/_Linux)

## Mount FS
`sudo memprocfs -device fpga -memmap auto -mount /mnt`

## Search patterm
Example for the string the [testbinary](/testbinary) generate
```
python3 scan.py /mnt/name/testbinary.exe-6448 --prefix "53 74 72 69 6E 67 3A 20" --pattern "$(printf '?? %.0s' {1..31})" --suffix "0D 0A"
Target VA: 0xE03DFFDF29 (unnamed)
Hex:  53 75 78 6d 53 70 77 6a 62 4c 4a 47 6c 69 61 4a 4f 6c 79 45 72 5a 53 6d 57 4c 66 4b 57 71 41
```

## ESP
The esp folder contains the most recent updates in this project, there will be every ESP project I will develop when I have free time.

