using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace SentonsPlatform
{
    class Program
    {
        
        static void Main(string[] args)
        {
            SentonsPlatform platform = new SentonsPlatform("User.txt", "Exp.txt");
            platform.Run();
            //while (true);
        }
    }
}
