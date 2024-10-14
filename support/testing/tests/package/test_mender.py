import os

import infra.basetest


class TestMenderInfra(infra.basetest.BRTest):
    config = infra.basetest.BASIC_TOOLCHAIN_CONFIG + \
             """
             BR2_PACKAGE_MENDER=y
             BR2_TARGET_ROOTFS_CPIO=y
             BR2_ROOTFS_OVERLAY="{}"
             """.format(
                 # overlay to add a fake 'fw_printenv', used by Mender
                 infra.filepath("tests/package/test_mender/rootfs-overlay"))

    def base_test_run(self):
        cpio_file = os.path.join(self.builddir, "images", "rootfs.cpio")
        self.emulator.boot(arch="armv5", kernel="builtin",
                           options=["-initrd", cpio_file])
        self.emulator.login()

    def run_mender_test(self):
        # Check if the Daemon is running
        self.assertRunOk("ls /var/run/mender.pid")
        self.assertRunOk("ps aux | egrep [m]ender")

        # Check if a simple Mender command is correctly executed
        self.assertRunOk("mender -log-level debug show-artifact")
        self.assertRunOk("mender -log-level debug show-artifact | grep 'RUNTIME_TEST_ARTIFACT_NAME'")
        cmd = "mender show-artifact 2>&1 | grep -i 'err'"  # Check if no 'error' among the traces
        _, exit_code = self.emulator.run(cmd)
        self.assertEqual(exit_code, 1)


class TestMenderRW(TestMenderInfra):
    def test_run(self):
        TestMenderInfra.base_test_run(self)
        self.run_mender_test()


class TestMenderRO(TestMenderInfra):
    config = \
        """
        {}
        # BR2_TARGET_GENERIC_REMOUNT_ROOTFS_RW is not set
        """.format(TestMenderInfra.config)

    def test_run(self):
        TestMenderInfra.base_test_run(self)
        self.run_mender_test()
