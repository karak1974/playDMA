# PlayDMA

> [!TIP]
> Before doing anything with this project I recommend reading the projects it's based on
[LeechCore](https://github.com/ufrisk/LeechCore)
[MemProcFS](https://github.com:ufrisk/memprocfs)
[pcileech](https://github.com:ufrisk/pcileech)

## Setup the DMA card
Install [OpenFPGALoader](https://github.com/trabucayre/openFPGALoader) and download the version for your card from [PCILeech-FPGA](https://github.com/ufrisk/pcileech-fpga), then upload the firmware to the SPI flash. In this example I'm flashing a CaptainDMA 75T.  
`openFPGALoader -c ch347_jtag -B -f ./pcileech_75t484_x1.bin`

## Install tools
Follow the guide at the [MemProcFS Wiki](https://github.com/ufrisk/MemProcFS/wiki/_Linux)

## Mount FS
`sudo memprocfs -device fpga -memmap auto -mount /mnt`

## Search patterm
Example for the string the [test binary](/test_binary) generate
```
python3 scan.py /mnt/name/testbinary.exe-6448 --prefix "53 74 72 69 6E 67 3A 20" --pattern "$(printf '?? %.0s' {1..31})" --suffix "0D 0A"
Target VA: 0xE03DFFDF29 (unnamed)
Hex:  53 75 78 6d 53 70 77 6a 62 4c 4a 47 6c 69 61 4a 4f 6c 79 45 72 5a 53 6d 57 4c 66 4b 57 71 41
```

