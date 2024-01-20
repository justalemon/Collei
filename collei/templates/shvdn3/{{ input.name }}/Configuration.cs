﻿using GTA.UI;
using System;
using System.Globalization;
using System.IO;
using System.Reflection;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;

namespace {{ input.name }};

/// <summary>
/// The configuration of the mod.
/// </summary>
internal class Configuration
{
    #region Fields

    private static readonly string path = Path.ChangeExtension(new Uri(Assembly.GetAssembly(typeof(Configuration)).CodeBase).LocalPath, ".json");
    private static readonly JsonSerializerSettings settings = new JsonSerializerSettings
    {
        ObjectCreationHandling = ObjectCreationHandling.Replace,
        Converters = [
            new StringEnumConverter()
        ],
        Formatting = Formatting.Indented,
        Culture = CultureInfo.InvariantCulture
    };
    
    #endregion
    
    #region Properties

    #endregion
    
    #region Functions
    
    /// <summary>
    /// Saves the configuration.
    /// </summary>
    public void Save()
    {
        string contents = JsonConvert.SerializeObject(this);
        File.WriteAllText(path, contents);
    }
    /// <summary>
    /// Gets the current configuration.
    /// </summary>
    /// <returns>The current configuration, or a new configuration if is not present.</returns>
    public static Configuration Load()
    {
        try
        {
            string contents = File.ReadAllText(path);
            return JsonConvert.DeserializeObject<Configuration>(contents, settings);
        }
        catch (FileNotFoundException)
        {
            Configuration config = new Configuration();
            config.Save();
            return config;
        }
        catch (Exception e)
        {
            Notification.Show($"~r~Error~w~: Unable to load config: {e.Message}");
            return new Configuration();
        }
    }
    
    #endregion
}
