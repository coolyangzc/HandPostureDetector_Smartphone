using System;
using System.IO;
using System.Threading;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SentonsPlatform
{
    public class SentonsReader
    {
        static TouchReader.Reader reader;
        static StreamWriter writer;
        static long startTime;
        Thread thread;

        public SentonsReader()
        {
            reader = new TouchReader.Reader();
        }

        static void print(string s)
        {
            System.Console.Write(s + '\n');
        }

        public void setWriter(StreamWriter swriter)
        {
            writer = swriter;
        }

        public void startRecord()
        {
            thread = new Thread(writing);
            thread.Start();
        }

        public void finishRecord()
        {
            thread.Abort();
        }

        static void writing()
        {
            int frame = 0;
            startTime = DateTime.Now.ToFileTime();
            while(true)
            {
                recordNewTouches(frame);
                frame++;
            }
        }

        static bool recordNewTouches(int frame)
        {
            TouchReader.TouchSet newestTouchSet;

            if (!reader.Read())
            {
                print(String.Format("Read: Error reported [ {0} ]", reader.Status));
                return false;
            }

            newestTouchSet = reader.LatestTouchSet;
            if (newestTouchSet.touchList.Count == 0)
                return true;

            writer.Write(string.Format("{0} {1} {2}", frame, DateTime.Now.ToFileTime() - startTime, newestTouchSet.touchList.Count));
            foreach (TouchReader.TouchReport touchReportEntry in newestTouchSet.touchList)
            {
                writer.Write(string.Format(" {0} {1} {2} {3} {4} {5}",
                            touchReportEntry.BarID, touchReportEntry.TrackID, touchReportEntry.force_lvl,
                            processSignedDiv16(touchReportEntry.pos0),
                            processSignedDiv16(touchReportEntry.pos1),
                            processSignedDiv16(touchReportEntry.pos2)));
            }
            writer.Write("\n");
            return true;
        }

        public bool connect()
        {
            if (reader.connect())
            {
                //print("Connect: Success");
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

        public bool read()
        {
            if (!reader.Connected)
            {
                print("Read: Connecting first.");
                if (!connect())
                {
                    print("Read: Failed, could not connect.");
                    return false;
                }
            }
            if (!getNewTouches())
            {
                print("Read: Failed, could not read tracks");
                return false;
            }
            return true;
        }

        public bool readAll()
        {
            if (!reader.Connected)
            {
                print("Read: Connecting first.");
                if (!reader.connect())
                {
                    print("Read: Failed, could not connect.");
                    return false;
                }
            }

            if (!getAllTouches())
            {
                print("Read: Failed, could not read tracks");
                return false;
            }
            return true;
        }

        public bool readAllWriteAll()
        {
            if (!reader.Connected)
            {
                print("Read: Connecting first.");
                if (!reader.connect())
                {
                    print("Read: Failed, could not connect.");
                    return false;
                }
            }

            if (!getAllTouches(true))
            {
                print("Read: Failed, could not read tracks");
                return false;
            }
            return true;
        }

        private bool getNewTouches()
        {
            TouchReader.TouchSet newestTouchSet;

            // Read the touches from the firmware
            if (!reader.Read())
            {
                print(String.Format("Read: Error reported [ {0} ]", reader.Status));
                return false;
            }

            // Retrieve the newest touches from the reader
            newestTouchSet = reader.LatestTouchSet;
            // Display my new touches (if any)
            printTouchSet(newestTouchSet);

            return true;
        }

        private bool getAllTouches(bool write = false)
        {
            // Read the touches from the firmware
            if (!reader.Read())
            {
                print(String.Format("Read: Error reported [ {0} ]", reader.Status));
                return false;
            }

            // Now print out all of the touchset that we just read in
            if (reader.touchSetList.Count == 0)
            {
                print("Read: no touches in buffer");
            }
            else
            {
                print(String.Format("We have read in {0} touch set(s):", reader.touchSetList.Count));
                foreach (TouchReader.TouchSet tset in reader.touchSetList)
                {
                    if (write)
                    {
                        writer.WriteLine("Bar ID, Track ID, Force, Pos0 mm, Pos1 mm, Pos2 mm");
                        foreach (TouchReader.TouchReport touchReportEntry in tset.touchList)
                        {
                            writer.WriteLine(string.Format("{0} {1} {2} {3} {4} {5}",
                                        touchReportEntry.BarID, touchReportEntry.TrackID, touchReportEntry.force_lvl,
                                        processSignedDiv16(touchReportEntry.pos0),
                                        processSignedDiv16(touchReportEntry.pos1),
                                        processSignedDiv16(touchReportEntry.pos2)));
                        }
                    }
                    else
                        printTouchSet(tset);
                }
            }
            return true;
        }

        private void printTouchSet(TouchReader.TouchSet tset)
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
