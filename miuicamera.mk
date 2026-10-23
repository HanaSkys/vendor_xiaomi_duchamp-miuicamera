PRODUCT_SOONG_NAMESPACES += vendor/xiaomi/duchamp-miuicamera

PRODUCT_PACKAGES += \
    MiuiCamera \
    libcamera_algoup_jni.xiaomi \
    libcamera_ispinterface_jni.xiaomi \
    libcamera_mianode_jni.xiaomi

PRODUCT_COPY_FILES += \
    vendor/xiaomi/duchamp-miuicamera/configs/privapp-permissions-miuicamera.xml:$(TARGET_COPY_OUT_SYSTEM_EXT)/etc/permissions/privapp-permissions-miuicamera.xml \
    vendor/xiaomi/duchamp-miuicamera/configs/public.libraries-xiaomi.txt:$(TARGET_COPY_OUT_SYSTEM_EXT)/etc/public.libraries-xiaomi.txt \
    vendor/xiaomi/duchamp-miuicamera/configs/miuicamera-hiddenapi-package-allowlist.xml:$(TARGET_COPY_OUT_SYSTEM_EXT)/etc/sysconfig/miuicamera-hiddenapi-package-allowlist.xml

PRODUCT_SYSTEM_EXT_PROPERTIES += \
    ro.com.google.lens.oem_camera_package=com.android.camera \
    ro.miui.notch=1

# isphal-V1-ndk (HyperOS) was built against graphics.common V6
PRODUCT_PACKAGES += \
    android.hardware.graphics.common-V6-ndk

# Mark MiuiCamera as a privileged camera client so cameraserver accepts
# vendor-only stream configurations (e.g. Y16 depth for portrait), which the
# HAL only advertises in com.xiaomi.scaler.availableStreamConfigurations.
PRODUCT_SYSTEM_EXT_PROPERTIES += \
    persist.vendor.camera.privapp.list=com.android.camera

# MiSys
PRODUCT_PACKAGES += \
    vendor.xiaomi.hardware.misys.common.service \
    vendor.xiaomi.hardware.misys.core.service
