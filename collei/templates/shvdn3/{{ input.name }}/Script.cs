using GTA;
using System;
using System.Windows.Forms;

namespace {{ input.name }};

public class {{ input.name }} : Script
{
    #region Fields

    private static readonly Configuration config = Configuration.Load();

    #endregion

    #region Constructors

    public {{ input.name }}()
    {
        Tick += OnTick;
        KeyDown += OnKeyDown;
        KeyUp += OnKeyUp;
        Aborted += OnAborted;
    }

    #endregion

    #region Event Functions

    private void OnTick(object sender, EventArgs e)
    {
    }
    private void OnKeyDown(object sender, KeyEventArgs e)
    {
    }
    private void OnKeyUp(object sender, KeyEventArgs e)
    {
    }
    private void OnAborted(object sender, EventArgs e)
    {
    }

    #endregion
}
