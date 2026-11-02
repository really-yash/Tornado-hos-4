#!/bin/sh
cd "$(dirname "$0")" || exit 1
fastboot=bin/linux/fastboot
[ ! -f $fastboot ] && echo "$fastboot not found." && exit 1
[ ! -x $fastboot ] && ! chmod +x $fastboot && echo "$fastboot cannot be executed." && exit 1
echo "Waiting for device..."
device=$($fastboot getvar product 2>&1 | grep -F "product:" | tr -s " " | cut -d " " -f 2)
[ -z "$device" ] && device="unknown"
[ "$device" != "tornado" ] && echo "Compatible devices: tornado" && echo "Your device: $device" && exit 1

echo "This install will delete all your applications, settings and files from internal storage."
printf "Do you agree? (Y/N) "
read -r choice
[ "$choice" != "y" ] && [ "$choice" != "Y" ] && exit 0

echo "###################################################"
echo "            HyperOs 4 Port by Yash               "
echo "###################################################"
$fastboot set_active a
$fastboot flash boot_a firmware-update/boot.img
$fastboot flash boot_b firmware-update/boot.img
$fastboot flash connsys_bt_a firmware-update/connsys_bt.img
$fastboot flash connsys_bt_b firmware-update/connsys_bt.img
$fastboot flash countrycode_a firmware-update/countrycode.img
$fastboot flash countrycode_b firmware-update/countrycode.img
$fastboot flash dpm_a firmware-update/dpm.img
$fastboot flash dpm_b firmware-update/dpm.img
$fastboot flash dtbo_a firmware-update/dtbo.img
$fastboot flash dtbo_b firmware-update/dtbo.img
$fastboot flash gz_a firmware-update/gz.img
$fastboot flash gz_b firmware-update/gz.img
$fastboot flash init_boot_a firmware-update/init_boot.img
$fastboot flash init_boot_b firmware-update/init_boot.img
$fastboot flash logo_a firmware-update/logo.bin
$fastboot flash logo_b firmware-update/logo.bin
$fastboot flash mcf_ota_a firmware-update/mcf_ota.img
$fastboot flash mcf_ota_b firmware-update/mcf_ota.img
$fastboot flash mcupm_a firmware-update/mcupm.img
$fastboot flash mcupm_b firmware-update/mcupm.img
$fastboot flash md1img_a firmware-update/md1img.img
$fastboot flash md1img_b firmware-update/md1img.img
$fastboot flash pi_img_a firmware-update/pi_img.img
$fastboot flash pi_img_b firmware-update/pi_img.img
$fastboot flash scp_a firmware-update/scp.img
$fastboot flash scp_b firmware-update/scp.img
$fastboot flash spmfw_a firmware-update/spmfw.img
$fastboot flash spmfw_b firmware-update/spmfw.img
$fastboot flash sspm_a firmware-update/sspm.img
$fastboot flash sspm_b firmware-update/sspm.img
$fastboot flash tee_a firmware-update/tee.img
$fastboot flash tee_b firmware-update/tee.img
$fastboot --disable-verity --disable-verification flash vbmeta_a firmware-update/vbmeta.img
$fastboot --disable-verity --disable-verification flash vbmeta_b firmware-update/vbmeta.img
$fastboot --disable-verity --disable-verification flash vbmeta_system_a firmware-update/vbmeta_system.img
$fastboot --disable-verity --disable-verification flash vbmeta_system_b firmware-update/vbmeta_system.img
$fastboot --disable-verity --disable-verification flash vbmeta_vendor_a firmware-update/vbmeta_vendor.img
$fastboot --disable-verity --disable-verification flash vbmeta_vendor_b firmware-update/vbmeta_vendor.img
$fastboot flash vcp_a firmware-update/vcp.img
$fastboot flash vcp_b firmware-update/vcp.img
$fastboot flash vendor_boot_a firmware-update/vendor_boot.img
$fastboot flash vendor_boot_b firmware-update/vendor_boot.img
$fastboot flash cust firmware-update/cust.img
$fastboot flash super firmware-update/super.img
$fastboot erase metadata
$fastboot erase userdata
$fastboot erase expdb
$fastboot oem cdms
$fastboot reboot
echo "-----------------------------"
echo "Finished! Reboot your device."
echo "-----------------------------"
