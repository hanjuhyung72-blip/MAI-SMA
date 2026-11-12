using System;
using System.IO;
using System.Net;
using System.Diagnostics;
using System.Threading;
using System.Windows.Forms;

class StudentKitLauncher {
    static string Root = AppDomain.CurrentDomain.BaseDirectory;
    static bool Ready(string url) {
        try {
            var request=(HttpWebRequest)WebRequest.Create(url+"api/info");
            request.Proxy=null; request.Timeout=1500;
            using(var response=request.GetResponse())
            using(var reader=new StreamReader(response.GetResponseStream())) {
                string value=reader.ReadToEnd();
                return value.Contains("MAI_SMA_student") && value.Contains("1000.duckdb");
            }
        } catch {return false;}
    }
    [STAThread] static void Main() {
        try {
            string package=Path.Combine(Root,"MAI_SMA_student");
            string pythonFile=Path.Combine(Root,"_runtime","python.path");
            string python=File.ReadAllText(pythonFile).Trim();
            if(!File.Exists(python))throw new Exception("실행용 Python 경로를 찾을 수 없습니다. _runtime/python.path를 Python 3.12 실행 파일 경로로 바꾸거나 제공된 START.bat을 사용하세요.");
            string url="http://127.0.0.1:8780/";
            if(!Ready(url)) {
                string logs=Path.Combine(package,"logs");Directory.CreateDirectory(logs);
                var start=new ProcessStartInfo();
                start.FileName=python;
                start.Arguments="-B \""+Path.Combine(package,"app","maintqa_web.py")+"\" --no-open --log \""+Path.Combine(logs,"maintqa_web.log")+"\"";
                start.WorkingDirectory=package;start.UseShellExecute=false;start.CreateNoWindow=true;start.WindowStyle=ProcessWindowStyle.Hidden;
                start.EnvironmentVariables["PYTHONPATH"]=Path.Combine(Root,"_runtime","site-packages");
                start.EnvironmentVariables["PYTHONDONTWRITEBYTECODE"]="1";
                start.EnvironmentVariables["PYTHONIOENCODING"]="utf-8";
                var process=Process.Start(start);bool ready=false;
                for(int i=0;i<180;i++) {
                    if(process.HasExited)throw new Exception("학생판 서버가 종료되었습니다. MAI_SMA_student/logs/maintqa_web.log를 확인하세요. 기존 300건 앱과는 별도의 프로그램입니다.");
                    if(Ready(url)){ready=true;break;}Thread.Sleep(500);
                }
                if(!ready)throw new Exception("서버 준비를 기다리는 중입니다. 잠시 후 http://127.0.0.1:8780/ 으로 접속하거나 로그를 확인하세요.");
            }
            try {
                Process.Start(new ProcessStartInfo(url){UseShellExecute=true});
            } catch(Exception browserError) {
                File.WriteAllText(Path.Combine(Root,"browser-open-note.txt"),browserError.Message);
                MessageBox.Show("학생판 서버가 준비되었습니다. 브라우저를 자동으로 열 수 없는 환경입니다. 브라우저 주소창에 다음 주소를 입력하세요.\n\n"+url,"MAI SMA 학생판",MessageBoxButtons.OK,MessageBoxIcon.Information);
            }
        } catch(Exception error) {
            File.WriteAllText(Path.Combine(Root,"launcher-error.txt"),error.ToString());
            MessageBox.Show(error.Message,"MAI SMA 학생판 실행",MessageBoxButtons.OK,MessageBoxIcon.Information);
        }
    }
}
