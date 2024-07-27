package org.dromara.hutool.core.io.file.common;

public class MD5Util {
    private final static String MD5_CMD_TEMPLATE = "certutil -hashfile %s MD5";

    public static String calcFileMD5InWin(String filePath) throws ExecCmdException {
        ExecuteShell.ExecResult execResult = ExecuteShell.execCmd(String.format(MD5_CMD_TEMPLATE, filePath), null);
        String[] outs = execResult.out.split(System.lineSeparator());
        if (execResult.process.exitValue() != 0) {
            throw new ExecCmdException("exitValue not 0, 【out=%s】, 【err=%s】", execResult.out, execResult.err);
        }
        return outs[1];
    }
}
