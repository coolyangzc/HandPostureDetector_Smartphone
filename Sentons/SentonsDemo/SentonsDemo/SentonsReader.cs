using System;
using System.IO;
using System.Net;
using System.Threading;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SentonsDemo
{
    public class SentonsReader
    {
        static TouchReader.Reader reader;
        static HttpListener httpListener;
        static Form1 form;
        static TouchReader.TouchSet newestTouchset;
        Thread thread;
        public SentonsReader(Form1 _form)
        {
            reader = new TouchReader.Reader();
            form = _form;
        }

        static void print(string s)
        {
            System.Console.Write(s + '\n');
        }

        public void startRead()
        {
            httpListener = new HttpListener();
            httpListener.AuthenticationSchemes = AuthenticationSchemes.Anonymous;
            httpListener.Prefixes.Add("http://127.0.0.1:8000/");
            httpListener.Start();
            thread = new Thread(reading);
            thread.Start();
        }

        public void finishRead()
        {
            if (httpListener != null)
                httpListener.Close();
            if (thread != null)
                thread.Abort();
        }

        static void reading(Object stateInfo)
        {
            while(true)
            {
                reader.Read();
                newestTouchset = reader.LatestTouchSet;
                string sendData = newestTouchset.touchList.Count.ToString();
                for (int i = 0; i < newestTouchset.touchList.Count; i++)
                {
                    TouchReader.TouchReport touchReportEntry = newestTouchset.touchList[i];
                    sendData += (string.Format(" {0} {1} {2} {3} {4} {5}",
                                touchReportEntry.BarID, touchReportEntry.TrackID, touchReportEntry.force_lvl,
                                processSignedDiv16(touchReportEntry.pos0),
                                processSignedDiv16(touchReportEntry.pos1),
                                processSignedDiv16(touchReportEntry.pos2)));
                }
                HttpListenerContext httpListenerContext = httpListener.GetContext();
                string type = httpListenerContext.Request.Url.ToString().Split('/')[3];
                httpListenerContext.Response.StatusCode = 200;
                if (type[0] == 't')
                {
                    using (StreamWriter writer = new StreamWriter(httpListenerContext.Response.OutputStream))
                    {
                        writer.Write(sendData);
                    }
                }
                else
                {
                    double result = double.Parse(type);
                    if (result == -1)
                        result = 0;
                    else if (result == 0)
                        result = -1;
                    form.Update(newestTouchset, result);
                    using (StreamWriter writer = new StreamWriter(httpListenerContext.Response.OutputStream))
                    {
                        writer.Write("");
                    }
                }
                Thread.Sleep(10);
            }
        }

        public bool connect()
        {
            if (reader.connect())
            {
                print("Connect: Success");
                return true;
            }
            print("Connect: ERROR");
            print(reader.Status);
            return false;
        }

        public bool disconnect()
        {
            if (reader.disconnect())
            {
                print("Disconnect: Success");
                return true;
            }
            print("Disconnect: ERROR");
            print(reader.Status);
            return false;
        }

        static private void printTouchSet(TouchReader.TouchSet tset)
        {
            if (tset.touchList.Count == 0)
            {
                print("Read: no current touches.");
            }
            else
            {
                print("Bar ID, Track ID, Force, Pos0 mm, Pos1 mm, Pos2 mm");
                foreach (TouchReader.TouchReport touchReportEntry in tset.touchList)
                {
                    print(string.Format("{0,6}, {1,8}, {2,5:F0}, {3,7:F2}, {4,7:F2}, {5,7:F2}",
                                touchReportEntry.BarID, touchReportEntry.TrackID, touchReportEntry.force_lvl,
                                processSignedDiv16(touchReportEntry.pos0),
                                processSignedDiv16(touchReportEntry.pos1),
                                processSignedDiv16(touchReportEntry.pos2)));
                }
            }
        }

        static public float processSignedDiv16(UInt16 data)
        {
            if (data <= 0x7FFF)
            {
                // We are positive
                return (Convert.ToSingle(data) / 16.0F);
            }
            // We are negative
            return ((Convert.ToSingle(data) - 0x10000) / 16.0F);
        }

    }
}
