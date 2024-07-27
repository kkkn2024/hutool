package org.dromara.hutool.core.io.file.common;

import org.apache.commons.lang3.StringUtils;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Locale;
import java.util.concurrent.TimeUnit;
import java.util.stream.Collectors;

public class ExecuteShell {
    private static final Logger log = LoggerFactory.getLogger(ExecuteShell.class);


    public static class ExecResult {
        public String out;
        public String err;
        public Process process;
    }

    public static ExecResult execCmd(String cmd, Integer timeoutSecond) throws ExecCmdException {
        if (timeoutSecond == null) {
            timeoutSecond = 10;
        }
        Charset charset = StandardCharsets.UTF_8;
        if (isWin()) {
            charset = Charset.forName("GBK");
        }
        try {
            Process process = new ProcessBuilder(Arrays.stream(cmd.split("\\s"))
                    .filter(StringUtils::isNotBlank)
                    .collect(Collectors.toList()))
//                .redirectErrorStream(true)
                    .start();

            ArrayList<String> outputs = new ArrayList<>();
            BufferedReader br = new BufferedReader(
                    new InputStreamReader(process.getInputStream(), charset));
            String line;
            while ((line = br.readLine()) != null) {
                outputs.add(line);
            }

            BufferedReader brErr = new BufferedReader(
                    new InputStreamReader(process.getErrorStream(), charset));
            ArrayList<String> errs = new ArrayList<>();
            while ((line = brErr.readLine()) != null) {
                errs.add(line);
            }

            ExecResult execResult = new ExecResult();
            execResult.out = String.join(System.lineSeparator(), outputs.toArray(new String[0]));
            execResult.err = String.join(System.lineSeparator(), errs.toArray(new String[0]));
            execResult.process = process;
            //There should really be a timeout here.
            if (!process.waitFor(timeoutSecond, TimeUnit.SECONDS)) {
                throw new ExecCmdException("process wait timeout, process=" + process + ", cmd=" + cmd);
            }
            return execResult;

        } catch (InterruptedException | IOException e) {
            throw new ExecCmdException(e);
        }
    }

    public static void execCmdWithoutOutput(String cmd) throws ExecCmdException {
        try {
            Process process = new ProcessBuilder(Arrays.stream(cmd.split("\\s"))
                    .filter(StringUtils::isNotBlank)
                    .collect(Collectors.toList()))
                    .start();
            log.info("cmd=" + cmd);
            log.info("process start pid=" + process.pid());
            // 不需要等待，运行一个不结束的进程，只有预期时间内会结束的进程才等待
//            if (!process.waitFor(timeoutSecond, TimeUnit.SECONDS)) {
//                throw new ExecCmdException("process wait timeout, process=" + process + ", cmd=" + cmd);
//            }
        } catch (IOException e) {
            throw new ExecCmdException(e);
        }
    }

    public static void main(String[] args) throws ExecCmdException {
        if (args != null && args.length >= 1) {
            String cmd = args[0];
            ExecResult execResult = execCmd(cmd, null);
            System.out.println("output: ---------------------\n" + execResult.out);
            if (execResult.err != null && !execResult.err.isEmpty()) {
                System.err.println("err: ---------------------\n" + execResult.err);
            }
        }

    }

    public static boolean isWin() {
        return System.getProperty("os.name").toLowerCase(Locale.ROOT).startsWith("win");
    }
}
